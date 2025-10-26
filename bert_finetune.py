import argparse
import os
from datasets import load_dataset, Dataset, DatasetDict
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    default_data_collator,
)
import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score

def parse_args():
    p = argparse.ArgumentParser(description='Fine-tune BERT for sequence classification')
    p.add_argument('--model_name', type=str, default='bert-base-uncased',
                        help='Hugging Face model name (default: bert-base-uncased)')
    p.add_argument('--train_file', default=None, help='Path to CSV/TSV train file with columns text,label')
    p.add_argument('--validation_file', default=None, help='Optional validation file (CSV/TSV)')
    p.add_argument('--output_dir', default='./fine_tuned_bert')
    p.add_argument('--num_labels', type=int, default=2)
    p.add_argument('--num_train_epochs', type=int, default=3)
    p.add_argument('--per_device_train_batch_size', type=int, default=8)
    p.add_argument('--learning_rate', type=float, default=2e-5)
    p.add_argument('--max_length', type=int, default=128)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--text_col', type=str, default=None, help='Column name for text in CSV/TSV')
    p.add_argument('--label_col', type=str, default=None, help='Column name for label in CSV/TSV')
    p.add_argument('--label_value', type=int, default=None, help='If specified, assign this label to all examples (0=Fake, 1=Real). Useful for single-class datasets.')
    p.add_argument('--delimiter', type=str, default=None, help='Delimiter for CSV/TSV (auto-detect if not provided)')
    return p.parse_args()


def compute_metrics(pred):
    preds = np.argmax(pred.predictions, axis=1)
    labels = pred.label_ids
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average='macro')
    return {'accuracy': acc, 'f1': f1}


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    # Set seed and device
    torch.manual_seed(args.seed)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=args.num_labels)
    model.to(device)

    # Set label mapping
    model.config.id2label = {0: 'Fake', 1: 'Real'}
    model.config.label2id = {'Fake': 0, 'Real': 1}

    # Load dataset
    if args.train_file:
        # try detect format
        data_files = {'train': args.train_file}
        if args.validation_file:
            data_files['validation'] = args.validation_file
        ext = os.path.splitext(args.train_file)[1].lower()
        # prefer csv loader; allow delimiter override
        load_kwargs = {}
        if args.delimiter:
            load_kwargs['delimiter'] = args.delimiter
        dataset = load_dataset('csv', data_files=data_files, **load_kwargs)
        # detect column names
        train_cols = dataset['train'].column_names
        # helper to choose column
        def detect_column(cols, preferred, candidates):
            if preferred and preferred in cols:
                return preferred
            for c in candidates:
                if c in cols:
                    return c
            return None

        text_candidates = ['text', 'sentence', 'content', 'article', 'body']
        label_candidates = ['label', 'labels', 'target', 'y']

        text_col = detect_column(train_cols, args.text_col, text_candidates)
        label_col = detect_column(train_cols, args.label_col, label_candidates)

        if text_col is None:
            raise ValueError(f'Could not detect text column. Found columns: {train_cols}. You can specify --text_col')

        # If no label column found but label_value specified, use it
        if label_col is None and args.label_value is not None:
            print(f'No label column found, using --label_value {args.label_value} for all examples')
            label_col = 'label'  # We'll add this column
        elif label_col is None:
            raise ValueError(f'Could not detect label column. Found columns: {train_cols}. You can specify --label_col or --label_value')

        # Normalize dataset column names to 'text' and 'label'
        def rename_columns(example):
            result = {'text': example[text_col]}
            if label_col in example:
                result['label'] = example[label_col]
            elif args.label_value is not None:
                result['label'] = args.label_value
            return result

        dataset = dataset.map(lambda ex: rename_columns(ex), batched=False)
        # normalize to DatasetDict
        if 'validation' not in dataset:
            # create a small split for validation
            dataset = dataset['train'].train_test_split(test_size=0.1, seed=args.seed)
            dataset = DatasetDict({'train': dataset['train'], 'validation': dataset['test']})
    else:
        # sample dataset (tiny) if no file provided
        texts = ["This is great!", "This is terrible!", "Amazing product", "Poor quality"]
        labels = [1, 0, 1, 0]
        dataset = Dataset.from_dict({'text': texts, 'label': labels})
        dataset = dataset.train_test_split(test_size=0.5, seed=args.seed)
        dataset = DatasetDict({'train': dataset['train'], 'validation': dataset['test']})

    # Tokenize function
    def tokenize_fn(ex):
        return tokenizer(ex['text'], truncation=True, padding='max_length', max_length=args.max_length)

    tokenized = dataset.map(tokenize_fn, batched=True)
    tokenized = tokenized.remove_columns([c for c in tokenized['train'].column_names if c not in ('input_ids','attention_mask','label')])

    # Training args
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        num_train_epochs=args.num_train_epochs,
        per_device_train_batch_size=args.per_device_train_batch_size,
        learning_rate=args.learning_rate,
        eval_strategy='epoch',
        save_strategy='epoch',
        logging_strategy='steps',
        logging_steps=50,
        load_best_model_at_end=True,
        fp16=torch.cuda.is_available(),
        seed=args.seed
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized['train'],
        eval_dataset=tokenized['validation'],
        tokenizer=tokenizer,
        data_collator=default_data_collator,
        compute_metrics=compute_metrics
    )

    # Train
    trainer.train()

    # Evaluate
    metrics = trainer.evaluate()
    print('Evaluation metrics:', metrics)

    # Save model and tokenizer
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print(f'Fine-tuned model saved to {args.output_dir}')


if __name__ == '__main__':
    main()

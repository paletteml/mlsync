import os
import torch
from datasets import load_dataset
from transformers import AutoTokenizer
from transformers import DataCollatorWithPadding
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
from mlsync.integrations.huggingface import MLSyncCallback

device = "cuda:0" if torch.cuda.is_available() else "cpu"

# The dataset
imdb = load_dataset("imdb")
# Tokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


def preprocess_function(examples):
    """tokenize text and truncate sequences to be no longer than DistilBERT’s maximum input length"""
    return tokenizer(examples["text"], truncation=True)


tokenized_imdb = imdb.map(preprocess_function, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Pre-trained Model
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

# Put model on GPU if available
model.to(device)

# MLSync Callback
mlsync_callback = MLSyncCallback(
    config="./config.yaml",
    format="./format.yaml",
    experiment_name="DistilBERT",
    run_name="DistilBERT-Base-Uncased",
    kpi="loss",
    kpi_direction="min",
    description="DistilBERT Base model for text classification.",
)

# Training Arguments
training_args = TrainingArguments(
    output_dir="./results",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_steps=100,
)

# Training
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_imdb["train"],
    eval_dataset=tokenized_imdb["test"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    callbacks=[mlsync_callback],
)

# Run training
trainer.train()

while True:
    input_text = input("Enter text: ")
    inputs = tokenizer(input_text, return_tensors="pt")
    with torch.no_grad():
        logits = model(**inputs).logits

    print(logits)
    predicted_class_id = logits.argmax().item()
    print(model.config.id2label[predicted_class_id])
    print(predicted_class_id)

import tensorflow as tf
from tensorflow import keras
import numpy as np
from pathlib import Path
import json

from ml.intent.model import IntentClassifier
from ml.training.data_generator import IntentDataGenerator


def create_training_data():
    data_gen = IntentDataGenerator()
    return data_gen.generate()


def train_model():
    print("Generating training data...")
    train_data, val_data, vocab_size, intent_map = create_training_data()
    
    X_train, y_train = train_data
    X_val, y_val = val_data
    
    print(f"Vocabulary size: {vocab_size}")
    print(f"Training samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    model = IntentClassifier(
        vocab_size=vocab_size,
        embedding_dim=128,
        num_intents=len(intent_map),
        max_length=50,
    )
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy'],
    )
    
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
        ),
    ]
    
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=30,
        batch_size=32,
        callbacks=callbacks,
        verbose=1,
    )
    
    models_dir = Path("models/saved_models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model.save(models_dir / "intent_classifier.keras")
    
    with open(models_dir / "intent_map.json", "w") as f:
        json.dump(intent_map, f, indent=2)
    
    print(f"Model saved to {models_dir}")
    print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
    
    return model, history


if __name__ == "__main__":
    train_model()


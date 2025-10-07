import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from typing import Dict, List


class IntentClassifier(keras.Model):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        num_intents: int = 7,
        max_length: int = 50,
    ):
        super().__init__()
        
        self.embedding = layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            mask_zero=True,
        )
        
        self.bidirectional_lstm = layers.Bidirectional(
            layers.LSTM(64, return_sequences=True)
        )
        
        self.attention = layers.MultiHeadAttention(
            num_heads=4,
            key_dim=64,
        )
        
        self.global_pool = layers.GlobalAveragePooling1D()
        
        self.dropout1 = layers.Dropout(0.3)
        self.dense1 = layers.Dense(128, activation='relu')
        
        self.dropout2 = layers.Dropout(0.2)
        self.dense2 = layers.Dense(64, activation='relu')
        
        self.output_layer = layers.Dense(num_intents, activation='softmax')
    
    def call(self, inputs, training=False):
        x = self.embedding(inputs)
        
        x = self.bidirectional_lstm(x, training=training)
        
        attention_output = self.attention(x, x, training=training)
        x = layers.Add()([x, attention_output])
        
        x = self.global_pool(x)
        
        x = self.dropout1(x, training=training)
        x = self.dense1(x)
        
        x = self.dropout2(x, training=training)
        x = self.dense2(x)
        
        return self.output_layer(x)
    
    def get_config(self):
        return {
            "vocab_size": self.embedding.input_dim,
            "embedding_dim": self.embedding.output_dim,
            "num_intents": self.output_layer.units,
        }


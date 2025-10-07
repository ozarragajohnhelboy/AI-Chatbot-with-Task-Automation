import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class EntityExtractor(keras.Model):
    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        num_entity_types: int = 10,
    ):
        super().__init__()
        
        self.embedding = layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            mask_zero=True,
        )
        
        self.bilstm_1 = layers.Bidirectional(
            layers.LSTM(128, return_sequences=True)
        )
        
        self.bilstm_2 = layers.Bidirectional(
            layers.LSTM(64, return_sequences=True)
        )
        
        self.dropout = layers.Dropout(0.3)
        
        self.dense = layers.Dense(64, activation='relu')
        
        self.crf_logits = layers.Dense(num_entity_types)
    
    def call(self, inputs, training=False):
        x = self.embedding(inputs)
        
        x = self.bilstm_1(x, training=training)
        x = self.bilstm_2(x, training=training)
        
        x = self.dropout(x, training=training)
        x = self.dense(x)
        
        return self.crf_logits(x)
    
    def get_config(self):
        return {
            "vocab_size": self.embedding.input_dim,
            "embedding_dim": self.embedding.output_dim,
            "num_entity_types": self.crf_logits.units,
        }


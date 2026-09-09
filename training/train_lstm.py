import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from training.data_preprocessing import load_and_preprocess_sensor_data
from config import Config

class WaterQualityLSTM(nn.Module):
    """
    LSTM Deep Learning Model for Temporal Water Quality Parameter Analysis.
    Captures sequential temporal dynamics across pH, Temp, Turbidity, DO, TDS, Conductivity.
    """
    def __init__(self, input_dim=6, hidden_dim=64, num_layers=2, num_classes=3, dropout=0.2):
        super(WaterQualityLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc1 = nn.Linear(hidden_dim, 32)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(32, num_classes)
        
    def forward(self, x):
        # x shape: [batch_size, seq_len, input_dim]
        lstm_out, _ = self.lstm(x)
        last_hidden = lstm_out[:, -1, :]
        features = self.relu(self.fc1(last_hidden))
        out = self.fc2(self.dropout(features))
        return out, features

def train_lstm_model(epochs=30, batch_size=32, lr=0.005, seq_length=4):
    """Trains and saves the temporal LSTM network."""
    X_train, X_test, y_train, y_test, _, feature_cols = load_and_preprocess_sensor_data()
    
    # Create smooth sequences with noise jitter for robust temporal learning
    def make_lstm_dataset(X, y, seq_len=4):
        seqs, labels = [], []
        for i in range(len(X)):
            # Build sequence leading up to point i
            hist = []
            for step in range(seq_len - 1, -1, -1):
                idx = max(0, i - step)
                hist.append(X[idx] + np.random.normal(0, 0.02, X[idx].shape))
            seqs.append(hist)
            labels.append(y[i])
        return np.array(seqs), np.array(labels)

    X_train_seq, y_train_seq = make_lstm_dataset(X_train, y_train, seq_len=seq_length)
    X_test_seq, y_test_seq = make_lstm_dataset(X_test, y_test, seq_len=seq_length)

    train_data = TensorDataset(torch.tensor(X_train_seq, dtype=torch.float32), torch.tensor(y_train_seq, dtype=torch.long))
    test_data = TensorDataset(torch.tensor(X_test_seq, dtype=torch.float32), torch.tensor(y_test_seq, dtype=torch.long))
    
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = WaterQualityLSTM(input_dim=len(feature_cols), hidden_dim=64, num_layers=2, num_classes=3).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    
    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs, _ = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

    # Evaluation
    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(device)
            outputs, _ = model(batch_x)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(batch_y.numpy())
            
    all_preds = np.array(all_preds)
    all_targets = np.array(all_targets)
    
    metrics = {
        'accuracy': round(float(accuracy_score(all_targets, all_preds) * 100), 2),
        'precision': round(float(precision_score(all_targets, all_preds, average='weighted', zero_division=0) * 100), 2),
        'recall': round(float(recall_score(all_targets, all_preds, average='weighted', zero_division=0) * 100), 2),
        'f1_score': round(float(f1_score(all_targets, all_preds, average='weighted', zero_division=0) * 100), 2),
        'seq_length': seq_length,
        'input_dim': len(feature_cols),
        'hidden_dim': 64,
        'num_layers': 2
    }
    
    save_dir = os.path.join(Config.MODELS_DIR, 'lstm_model')
    os.makedirs(save_dir, exist_ok=True)
    
    torch.save(model.state_dict(), os.path.join(save_dir, 'lstm_water_quality.pth'))
    with open(os.path.join(save_dir, 'lstm_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"[LSTM] Training finished -> Acc: {metrics['accuracy']}%, F1: {metrics['f1_score']}%")
    return model, metrics

if __name__ == '__main__':
    train_lstm_model()

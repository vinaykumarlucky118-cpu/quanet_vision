import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from config import Config

class SatelliteCNN(nn.Module):
    """
    Convolutional Neural Network for Satellite Water Body Visual Feature Extraction.
    Extracts deep spatial textures, algal dispersion, and turbidity gradients.
    """
    def __init__(self, num_classes=3, embedding_dim=32):
        super(SatelliteCNN, self).__init__()
        self.embedding_dim = embedding_dim
        
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2), # 64x64
            
            # Block 2
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2), # 32x32
            
            # Block 3
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((4, 4)) # 64 * 4 * 4 = 1024
        )
        
        self.fc_embed = nn.Sequential(
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, embedding_dim),
            nn.ReLU(inplace=True)
        )
        
        self.classifier = nn.Linear(embedding_dim, num_classes)
        
    def forward(self, x):
        feat_map = self.features(x)
        flat = feat_map.view(feat_map.size(0), -1)
        embeddings = self.fc_embed(flat)
        logits = self.classifier(embeddings)
        return logits, embeddings

def generate_synthetic_satellite_images(output_dir, num_samples_per_class=40):
    """Generates realistic synthetic satellite imagery tiles for Good, Moderate, and Poor water quality."""
    os.makedirs(output_dir, exist_ok=True)
    image_records = []
    
    classes = [
        {"label": "GOOD", "target": 0, "color_base": (25, 65, 120), "noise_color": (30, 90, 140), "desc": "Clear deep oligotrophic water body"},
        {"label": "MODERATE", "target": 1, "color_base": (75, 110, 85), "noise_color": (120, 140, 90), "desc": "Mesotrophic water body with mild sediment suspended load"},
        {"label": "POOR", "target": 2, "color_base": (120, 95, 45), "noise_color": (45, 135, 40), "desc": "Eutrophic water body with high sediment & algae bloom"}
    ]
    
    for cls in classes:
        cls_dir = os.path.join(output_dir, cls["label"].lower())
        os.makedirs(cls_dir, exist_ok=True)
        
        for i in range(num_samples_per_class):
            img_size = (128, 128)
            img = Image.new("RGB", img_size, cls["color_base"])
            draw = ImageDraw.Draw(img)
            
            # Add spatial ripple / texture noise
            for _ in range(35):
                x1 = np.random.randint(0, 128)
                y1 = np.random.randint(0, 128)
                r = np.random.randint(5, 25)
                c_noise = tuple(np.clip(np.array(cls["noise_color"]) + np.random.randint(-20, 20, 3), 0, 255))
                draw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=c_noise, outline=None)
                
            img = img.filter(ImageFilter.GaussianBlur(radius=np.random.uniform(1.0, 3.0)))
            
            filename = f"{cls['label'].lower()}_sat_{i+1:03d}.jpg"
            filepath = os.path.join(cls_dir, filename)
            img.save(filepath, "JPEG", quality=90)
            
            image_records.append({
                "filepath": filepath,
                "filename": filename,
                "label": cls["label"],
                "target": cls["target"]
            })
            
    return image_records

class SatelliteImageDataset(Dataset):
    def __init__(self, records):
        self.records = records
        
    def __len__(self):
        return len(self.records)
        
    def __getitem__(self, idx):
        item = self.records[idx]
        img = Image.open(item["filepath"]).convert("RGB").resize((128, 128))
        img_np = np.array(img, dtype=np.float32) / 255.0
        # Change HWC to CHW
        img_tensor = torch.tensor(img_np).permute(2, 0, 1)
        # Normalize (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        img_norm = (img_tensor - mean) / std
        
        return img_norm, item["target"]

def train_cnn_model(epochs=25, batch_size=16, lr=0.001):
    """Trains the Satellite CNN model and saves weights & metrics."""
    sat_dir = os.path.join(Config.DATASET_DIR, 'satellite_images')
    records = generate_synthetic_satellite_images(sat_dir, num_samples_per_class=45)
    
    # Split train/test
    np.random.seed(42)
    np.random.shuffle(records)
    split_idx = int(0.8 * len(records))
    train_records = records[:split_idx]
    test_records = records[split_idx:]
    
    train_dataset = SatelliteImageDataset(train_records)
    test_dataset = SatelliteImageDataset(test_records)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = SatelliteCNN(num_classes=3, embedding_dim=32).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    
    model.train()
    for epoch in range(epochs):
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            optimizer.zero_grad()
            logits, _ = model(imgs)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            
    # Evaluate
    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs = imgs.to(device)
            logits, _ = model(imgs)
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(labels.numpy())
            
    metrics = {
        'accuracy': round(float(accuracy_score(all_targets, all_preds) * 100), 2),
        'precision': round(float(precision_score(all_targets, all_preds, average='weighted', zero_division=0) * 100), 2),
        'recall': round(float(recall_score(all_targets, all_preds, average='weighted', zero_division=0) * 100), 2),
        'f1_score': round(float(f1_score(all_targets, all_preds, average='weighted', zero_division=0) * 100), 2),
        'architecture': 'Conv2D-BatchNorm-ReLU-MaxPool-AdaptiveAvgPool-FC',
        'embedding_dim': 32,
        'input_resolution': '128x128x3'
    }
    
    save_dir = os.path.join(Config.MODELS_DIR, 'cnn_model')
    os.makedirs(save_dir, exist_ok=True)
    
    torch.save(model.state_dict(), os.path.join(save_dir, 'cnn_satellite.pth'))
    with open(os.path.join(save_dir, 'cnn_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print(f"[CNN] Training finished -> Acc: {metrics['accuracy']}%, F1: {metrics['f1_score']}%")
    return model, metrics

if __name__ == '__main__':
    train_cnn_model()

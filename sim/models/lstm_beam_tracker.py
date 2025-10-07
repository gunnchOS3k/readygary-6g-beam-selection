"""
LSTM-based Beam Tracking
Addresses professor feedback: "use ML in a more complex scenario like tracking"
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, top_k_accuracy_score

class BeamTrackingDataset(Dataset):
    """Dataset for beam tracking with temporal sequences"""
    
    def __init__(self, sequences: List[np.ndarray], targets: List[int], 
                 sequence_length: int = 10):
        self.sequences = sequences
        self.targets = targets
        self.sequence_length = sequence_length
        
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        target = self.targets[idx]
        return torch.FloatTensor(sequence), torch.LongTensor([target])

class LSTMBeamTracker(nn.Module):
    """
    LSTM-based beam tracking model
    Predicts optimal beam based on historical CSI and mobility
    """
    
    def __init__(self, input_size: int = 256, hidden_size: int = 128, 
                 num_layers: int = 2, num_beams: int = 64, dropout: float = 0.2):
        super(LSTMBeamTracker, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_beams = num_beams
        
        # LSTM layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=dropout)
        
        # Attention mechanism
        self.attention = nn.Linear(hidden_size, 1)
        
        # Output layers
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, num_beams)
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Attention mechanism
        attention_weights = torch.softmax(self.attention(lstm_out), dim=1)
        attended_output = torch.sum(lstm_out * attention_weights, dim=1)
        
        # Classification head
        x = self.dropout(attended_output)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x

class BeamTracker:
    """Beam tracking system with LSTM model"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.sequence_buffer = []
        self.sequence_length = 10
        
        if model_path:
            self.load_model(model_path)
    
    def prepare_training_data(self, channels: List[np.ndarray], 
                            optimal_beams: List[Tuple[int, int]]) -> Tuple[List, List]:
        """Prepare training data for beam tracking"""
        sequences = []
        targets = []
        
        for i in range(len(channels) - self.sequence_length):
            # Extract CSI features from channel matrix
            csi_features = self.extract_csi_features(channels[i:i+self.sequence_length])
            sequences.append(csi_features)
            
            # Target is the optimal beam for the next time step
            target_beam = optimal_beams[i + self.sequence_length][0]  # TX beam
            targets.append(target_beam)
        
        return sequences, targets
    
    def extract_csi_features(self, channel_sequence: List[np.ndarray]) -> np.ndarray:
        """Extract CSI features from channel sequence"""
        features = []
        
        for H in channel_sequence:
            # Channel magnitude and phase
            magnitude = np.abs(H).flatten()
            phase = np.angle(H).flatten()
            
            # Channel statistics
            mean_mag = np.mean(magnitude)
            std_mag = np.std(magnitude)
            max_mag = np.max(magnitude)
            
            # Combine features
            channel_features = np.concatenate([
                magnitude, phase, [mean_mag, std_mag, max_mag]
            ])
            features.append(channel_features)
        
        return np.array(features)
    
    def train(self, channels: List[np.ndarray], optimal_beams: List[Tuple[int, int]], 
              epochs: int = 100, batch_size: int = 32, learning_rate: float = 0.001):
        """Train the LSTM beam tracker"""
        print("🚀 Training LSTM Beam Tracker...")
        
        # Prepare data
        sequences, targets = self.prepare_training_data(channels, optimal_beams)
        
        # Create dataset and dataloader
        dataset = BeamTrackingDataset(sequences, targets, self.sequence_length)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize model
        input_size = sequences[0].shape[1]
        self.model = LSTMBeamTracker(input_size=input_size, num_beams=64)
        self.model.to(self.device)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)
        
        # Training loop
        train_losses = []
        train_accuracies = []
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            epoch_correct = 0
            epoch_total = 0
            
            for batch_sequences, batch_targets in dataloader:
                batch_sequences = batch_sequences.to(self.device)
                batch_targets = batch_targets.squeeze().to(self.device)
                
                # Forward pass
                optimizer.zero_grad()
                outputs = self.model(batch_sequences)
                loss = criterion(outputs, batch_targets)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                # Statistics
                epoch_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                epoch_total += batch_targets.size(0)
                epoch_correct += (predicted == batch_targets).sum().item()
            
            # Epoch statistics
            avg_loss = epoch_loss / len(dataloader)
            accuracy = 100 * epoch_correct / epoch_total
            
            train_losses.append(avg_loss)
            train_accuracies.append(accuracy)
            
            scheduler.step(avg_loss)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch:3d}: Loss = {avg_loss:.4f}, Accuracy = {accuracy:.2f}%")
        
        # Plot training curves
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(train_losses)
        plt.title('Training Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(1, 2, 2)
        plt.plot(train_accuracies)
        plt.title('Training Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy (%)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('docs/figs/lstm_training_curves.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✅ Training completed! Model saved to docs/figs/lstm_training_curves.png")
    
    def predict_beam(self, channel_sequence: List[np.ndarray]) -> int:
        """Predict optimal beam for given channel sequence"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        self.model.eval()
        with torch.no_grad():
            # Extract features
            csi_features = self.extract_csi_features(channel_sequence)
            csi_tensor = torch.FloatTensor(csi_features).unsqueeze(0).to(self.device)
            
            # Predict
            outputs = self.model(csi_tensor)
            _, predicted = torch.max(outputs, 1)
            
            return predicted.item()
    
    def evaluate(self, test_channels: List[np.ndarray], 
                test_optimal_beams: List[Tuple[int, int]]) -> Dict:
        """Evaluate beam tracker performance"""
        print("📊 Evaluating LSTM Beam Tracker...")
        
        predictions = []
        targets = []
        
        for i in range(len(test_channels) - self.sequence_length):
            # Get sequence
            sequence = test_channels[i:i+self.sequence_length]
            target = test_optimal_beams[i + self.sequence_length][0]
            
            # Predict
            predicted = self.predict_beam(sequence)
            predictions.append(predicted)
            targets.append(target)
        
        # Calculate metrics
        accuracy = accuracy_score(targets, predictions)
        top2_accuracy = top_k_accuracy_score(targets, predictions, k=2)
        top4_accuracy = top_k_accuracy_score(targets, predictions, k=4)
        
        results = {
            'accuracy': accuracy,
            'top2_accuracy': top2_accuracy,
            'top4_accuracy': top4_accuracy,
            'predictions': predictions,
            'targets': targets
        }
        
        print(f"📈 Results:")
        print(f"   Top-1 Accuracy: {accuracy:.3f}")
        print(f"   Top-2 Accuracy: {top2_accuracy:.3f}")
        print(f"   Top-4 Accuracy: {top4_accuracy:.3f}")
        
        return results
    
    def save_model(self, path: str):
        """Save trained model"""
        torch.save(self.model.state_dict(), path)
        print(f"✅ Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model"""
        self.model = LSTMBeamTracker()
        self.model.load_state_dict(torch.load(path))
        self.model.to(self.device)
        print(f"✅ Model loaded from {path}")

def main():
    """Main training and evaluation script"""
    print("🧠 ReadyGary LSTM Beam Tracker")
    print("=" * 50)
    
    # Generate training data
    from exhaustive_search import generate_tdl_channels, ExhaustiveBeamSearch
    
    print("📡 Generating training data...")
    channels = generate_tdl_channels(num_channels=2000)
    
    # Find optimal beams using exhaustive search
    print("🔍 Finding optimal beams...")
    searcher = ExhaustiveBeamSearch()
    optimal_beams = []
    
    for i, H in enumerate(channels):
        if i % 100 == 0:
            print(f"   Processed {i}/{len(channels)} channels")
        tx_beam, rx_beam, snr, _ = searcher.search_optimal_beams(H)
        optimal_beams.append((tx_beam, rx_beam))
    
    # Split data
    split_idx = int(0.8 * len(channels))
    train_channels = channels[:split_idx]
    train_beams = optimal_beams[:split_idx]
    test_channels = channels[split_idx:]
    test_beams = optimal_beams[split_idx:]
    
    # Train model
    tracker = BeamTracker()
    tracker.train(train_channels, train_beams, epochs=50)
    
    # Evaluate
    results = tracker.evaluate(test_channels, test_beams)
    
    # Save model
    tracker.save_model('models/lstm_beam_tracker.pth')
    
    print(f"\n✅ LSTM Beam Tracker training and evaluation completed!")

if __name__ == "__main__":
    main()
EOF'
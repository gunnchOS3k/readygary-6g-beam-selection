"""
Dataset Generation Script
Incorporates professor feedback: "use TDL channel as you suggest or ray tracing"
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import pickle
import os
from dataclasses import dataclass

@dataclass
class ChannelConfig:
    """Configuration for channel generation"""
    num_channels: int = 10000
    num_tx_ant: int = 8
    num_rx_ant: int = 8
    carrier_freq: float = 28e9  # 28 GHz
    num_paths: Tuple[int, int] = (3, 8)  # Min, max paths
    path_loss_range: Tuple[float, float] = (0.1, 2.0)
    mobility_speed: float = 1.0  # m/s
    coherence_time: float = 0.1  # seconds

class TDLChannelGenerator:
    """
    TDL Channel Generator
    Addresses professor feedback about using realistic channel models
    """
    
    def __init__(self, config: ChannelConfig):
        self.config = config
        self.wavelength = 3e8 / config.carrier_freq
        
    def generate_tdl_channel(self, user_position: np.ndarray, 
                           base_station_position: np.ndarray,
                           mobility_vector: np.ndarray = None) -> np.ndarray:
        """Generate TDL channel with realistic ray paths"""
        
        # Calculate distance and angles
        distance = np.linalg.norm(user_position - base_station_position)
        path_loss = self._calculate_path_loss(distance)
        
        # Generate multiple paths
        num_paths = np.random.randint(self.config.num_paths[0], self.config.num_paths[1])
        H = np.zeros((self.config.num_tx_ant, self.config.num_rx_ant), dtype=complex)
        
        for _ in range(num_paths):
            # Random path parameters
            tx_angle = np.random.uniform(0, 2*np.pi)
            rx_angle = np.random.uniform(0, 2*np.pi)
            path_gain = np.random.exponential(1.0) * path_loss
            phase = np.random.uniform(0, 2*np.pi)
            
            # Add mobility effect
            if mobility_vector is not None:
                doppler_shift = np.dot(mobility_vector, [np.cos(tx_angle), np.sin(tx_angle)])
                phase += 2 * np.pi * doppler_shift * self.config.coherence_time
            
            # Create steering vectors
            tx_steering = self._create_steering_vector(tx_angle, self.config.num_tx_ant)
            rx_steering = self._create_steering_vector(rx_angle, self.config.num_rx_ant)
            
            # Add path contribution
            H += path_gain * np.exp(1j * phase) * np.outer(tx_steering, rx_steering)
        
        return H
    
    def _calculate_path_loss(self, distance: float) -> float:
        """Calculate path loss using free space + additional losses"""
        # Free space path loss
        fspl = (4 * np.pi * distance / self.wavelength) ** 2
        
        # Additional losses (shadowing, etc.)
        shadowing = np.random.normal(0, 8)  # 8 dB standard deviation
        
        total_loss = fspl * 10 ** (shadowing / 10)
        return 1.0 / np.sqrt(total_loss)
    
    def _create_steering_vector(self, angle: float, num_antennas: int) -> np.ndarray:
        """Create steering vector for uniform linear array"""
        antenna_spacing = self.wavelength / 2
        steering_vector = np.array([
            np.exp(1j * 2 * np.pi * i * antenna_spacing * np.cos(angle) / self.wavelength)
            for i in range(num_antennas)
        ])
        return steering_vector / np.sqrt(num_antennas)
    
    def generate_mobility_sequence(self, initial_position: np.ndarray, 
                                 num_steps: int = 100) -> List[np.ndarray]:
        """Generate mobility sequence for beam tracking"""
        positions = [initial_position]
        velocities = []
        
        for _ in range(num_steps - 1):
            # Random walk mobility
            velocity = np.random.normal(0, self.config.mobility_speed, 2)
            velocities.append(velocity)
            
            # Update position
            new_position = positions[-1] + velocity * self.config.coherence_time
            positions.append(new_position)
        
        return positions, velocities

class DatasetGenerator:
    """Main dataset generator"""
    
    def __init__(self, config: ChannelConfig):
        self.config = config
        self.generator = TDLChannelGenerator(config)
    
    def generate_static_dataset(self) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        """Generate static channel dataset"""
        print("📡 Generating static TDL channels...")
        
        channels = []
        optimal_beams = []
        
        for i in range(self.config.num_channels):
            if i % 1000 == 0:
                print(f"   Generated {i}/{self.config.num_channels} channels")
            
            # Random positions
            user_pos = np.random.uniform(-100, 100, 2)
            bs_pos = np.random.uniform(-50, 50, 2)
            
            # Generate channel
            H = self.generator.generate_tdl_channel(user_pos, bs_pos)
            channels.append(H)
            
            # Find optimal beam (simplified)
            optimal_beam = self._find_optimal_beam_simple(H)
            optimal_beams.append(optimal_beam)
        
        return channels, optimal_beams
    
    def generate_mobility_dataset(self) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        """Generate mobility dataset for beam tracking"""
        print("📡 Generating mobility TDL channels...")
        
        channels = []
        optimal_beams = []
        
        num_users = self.config.num_channels // 100  # 100 steps per user
        
        for user in range(num_users):
            if user % 10 == 0:
                print(f"   Generated {user}/{num_users} users")
            
            # Random initial position
            initial_pos = np.random.uniform(-100, 100, 2)
            bs_pos = np.random.uniform(-50, 50, 2)
            
            # Generate mobility sequence
            positions, velocities = self.generator.generate_mobility_sequence(initial_pos)
            
            for step, (pos, vel) in enumerate(zip(positions, velocities)):
                # Generate channel for this position
                H = self.generator.generate_tdl_channel(pos, bs_pos, vel)
                channels.append(H)
                
                # Find optimal beam
                optimal_beam = self._find_optimal_beam_simple(H)
                optimal_beams.append(optimal_beam)
        
        return channels, optimal_beams
    
    def _find_optimal_beam_simple(self, H: np.ndarray) -> Tuple[int, int]:
        """Simplified optimal beam finding"""
        # Generate codebooks
        tx_codebook = self._generate_codebook(64, self.config.num_tx_ant)
        rx_codebook = self._generate_codebook(64, self.config.num_rx_ant)
        
        max_snr = 0.0
        best_tx = 0
        best_rx = 0
        
        # Search through all combinations
        for tx_idx in range(64):
            for rx_idx in range(64):
                snr = np.abs(tx_codebook[tx_idx] @ H @ rx_codebook[rx_idx]) ** 2
                if snr > max_snr:
                    max_snr = snr
                    best_tx = tx_idx
                    best_rx = rx_idx
        
        return best_tx, best_rx
    
    def _generate_codebook(self, num_beams: int, num_antennas: int) -> np.ndarray:
        """Generate DFT codebook"""
        codebook = np.zeros((num_beams, num_antennas), dtype=complex)
        for i in range(num_beams):
            for j in range(num_antennas):
                codebook[i, j] = np.exp(1j * 2 * np.pi * i * j / num_beams)
        return codebook / np.sqrt(num_antennas)
    
    def save_dataset(self, channels: List[np.ndarray], beams: List[Tuple[int, int]], 
                    filename: str):
        """Save dataset to file"""
        dataset = {
            'channels': channels,
            'optimal_beams': beams,
            'config': self.config
        }
        
        os.makedirs('data/processed', exist_ok=True)
        with open(f'data/processed/{filename}', 'wb') as f:
            pickle.dump(dataset, f)
        
        print(f"✅ Dataset saved to data/processed/{filename}")
    
    def load_dataset(self, filename: str) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
        """Load dataset from file"""
        with open(f'data/processed/{filename}', 'rb') as f:
            dataset = pickle.load(f)
        
        return dataset['channels'], dataset['optimal_beams']

def main():
    """Main dataset generation script"""
    print("📊 ReadyGary Dataset Generation")
    print("=" * 50)
    
    # Configuration
    config = ChannelConfig(
        num_channels=10000,
        num_tx_ant=8,
        num_rx_ant=8,
        carrier_freq=28e9,
        mobility_speed=1.0
    )
    
    # Initialize generator
    generator = DatasetGenerator(config)
    
    # Generate static dataset
    print("🔄 Generating static dataset...")
    static_channels, static_beams = generator.generate_static_dataset()
    generator.save_dataset(static_channels, static_beams, 'static_tdl_dataset.pkl')
    
    # Generate mobility dataset
    print("🔄 Generating mobility dataset...")
    mobility_channels, mobility_beams = generator.generate_mobility_dataset()
    generator.save_dataset(mobility_channels, mobility_beams, 'mobility_tdl_dataset.pkl')
    
    # Generate summary plots
    print("📈 Generating summary plots...")
    
    plt.figure(figsize=(15, 5))
    
    # Channel magnitude distribution
    plt.subplot(1, 3, 1)
    magnitudes = [np.abs(H).flatten() for H in static_channels[:1000]]
    all_magnitudes = np.concatenate(magnitudes)
    plt.hist(all_magnitudes, bins=50, alpha=0.7)
    plt.xlabel('Channel Magnitude')
    plt.ylabel('Frequency')
    plt.title('Channel Magnitude Distribution')
    plt.grid(True, alpha=0.3)
    
    # Beam distribution
    plt.subplot(1, 3, 2)
    tx_beams = [beam[0] for beam in static_beams]
    rx_beams = [beam[1] for beam in static_beams]
    plt.scatter(tx_beams, rx_beams, alpha=0.6)
    plt.xlabel('TX Beam Index')
    plt.ylabel('RX Beam Index')
    plt.title('Optimal Beam Distribution')
    plt.grid(True, alpha=0.3)
    
    # SNR distribution
    plt.subplot(1, 3, 3)
    snr_values = []
    for H, (tx_beam, rx_beam) in zip(static_channels[:1000], static_beams[:1000]):
        tx_vec = generator._generate_codebook(64, 8)[tx_beam]
        rx_vec = generator._generate_codebook(64, 8)[rx_beam]
        snr = np.abs(tx_vec @ H @ rx_vec) ** 2
        snr_values.append(10 * np.log10(snr))
    
    plt.hist(snr_values, bins=50, alpha=0.7)
    plt.xlabel('SNR (dB)')
    plt.ylabel('Frequency')
    plt.title('SNR Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('docs/figs/dataset_summary.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n✅ Dataset generation completed!")
    print(f"   Static dataset: {len(static_channels)} channels")
    print(f"   Mobility dataset: {len(mobility_channels)} channels")
    print(f"   Summary plots saved to docs/figs/dataset_summary.png")

if __name__ == "__main__":
    main()
EOF'
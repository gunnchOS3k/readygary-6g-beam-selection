"""
Exhaustive Beam Search Baseline
Addresses professor feedback: "baseline algorithm should simply search all algorithms"
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict
import time

class ExhaustiveBeamSearch:
    """
    Baseline exhaustive search through all possible beam combinations.
    This is the oracle baseline that ML should approach.
    """
    
    def __init__(self, num_tx_beams: int = 64, num_rx_beams: int = 64):
        self.num_tx_beams = num_tx_beams
        self.num_rx_beams = num_rx_beams
        self.search_time = 0.0
        
    def generate_codebook(self, num_beams: int, num_antennas: int = 8) -> np.ndarray:
        """Generate DFT codebook for beamforming"""
        codebook = np.zeros((num_beams, num_antennas), dtype=complex)
        for i in range(num_beams):
            # DFT beamforming weights
            for j in range(num_antennas):
                codebook[i, j] = np.exp(1j * 2 * np.pi * i * j / num_beams)
        return codebook / np.sqrt(num_antennas)
    
    def compute_snr(self, H: np.ndarray, tx_beam: np.ndarray, rx_beam: np.ndarray) -> float:
        """Compute SNR for given channel and beam pair"""
        # Apply beamforming
        tx_signal = tx_beam @ H @ rx_beam
        # SNR = |signal|^2 / noise_power (assuming unit noise)
        snr = np.abs(tx_signal) ** 2
        return snr
    
    def search_optimal_beams(self, H: np.ndarray) -> Tuple[int, int, float, float]:
        """
        Exhaustive search for optimal beam pair
        Returns: (best_tx_beam, best_rx_beam, max_snr, search_time)
        """
        start_time = time.time()
        
        # Generate codebooks
        tx_codebook = self.generate_codebook(self.num_tx_beams)
        rx_codebook = self.generate_codebook(self.num_rx_beams)
        
        max_snr = 0.0
        best_tx_idx = 0
        best_rx_idx = 0
        
        # Exhaustive search through all combinations
        for tx_idx in range(self.num_tx_beams):
            for rx_idx in range(self.num_rx_beams):
                snr = self.compute_snr(H, tx_codebook[tx_idx], rx_codebook[rx_idx])
                if snr > max_snr:
                    max_snr = snr
                    best_tx_idx = tx_idx
                    best_rx_idx = rx_idx
        
        search_time = time.time() - start_time
        self.search_time = search_time
        
        return best_tx_idx, best_rx_idx, max_snr, search_time
    
    def evaluate_performance(self, channels: List[np.ndarray]) -> Dict:
        """Evaluate exhaustive search performance"""
        results = {
            'beam_pairs': [],
            'snr_values': [],
            'search_times': [],
            'total_time': 0.0
        }
        
        start_time = time.time()
        
        for i, H in enumerate(channels):
            tx_beam, rx_beam, snr, search_time = self.search_optimal_beams(H)
            results['beam_pairs'].append((tx_beam, rx_beam))
            results['snr_values'].append(snr)
            results['search_times'].append(search_time)
            
            if i % 100 == 0:
                print(f"Processed {i+1}/{len(channels)} channels")
        
        results['total_time'] = time.time() - start_time
        results['avg_search_time'] = np.mean(results['search_times'])
        results['avg_snr'] = np.mean(results['snr_values'])
        
        return results

def generate_tdl_channels(num_channels: int = 1000, 
                         num_tx_ant: int = 8, 
                         num_rx_ant: int = 8,
                         carrier_freq: float = 28e9) -> List[np.ndarray]:
    """
    Generate realistic TDL channel matrices (addressing professor feedback)
    Using actual ray-based channels instead of iid matrices
    """
    channels = []
    
    for _ in range(num_channels):
        # Generate realistic channel with multiple paths
        num_paths = np.random.randint(3, 8)  # 3-7 paths
        H = np.zeros((num_tx_ant, num_rx_ant), dtype=complex)
        
        for _ in range(num_paths):
            # Random path parameters
            tx_angle = np.random.uniform(0, 2*np.pi)
            rx_angle = np.random.uniform(0, 2*np.pi)
            path_loss = np.random.exponential(1.0)
            phase = np.random.uniform(0, 2*np.pi)
            
            # Create steering vectors
            tx_steering = np.array([np.exp(1j * 2 * np.pi * i * np.cos(tx_angle) / 2) 
                                  for i in range(num_tx_ant)])
            rx_steering = np.array([np.exp(1j * 2 * np.pi * i * np.cos(rx_angle) / 2) 
                                  for i in range(num_rx_ant)])
            
            # Add path contribution
            H += path_loss * np.exp(1j * phase) * np.outer(tx_steering, rx_steering)
        
        channels.append(H)
    
    return channels

def main():
    """Main evaluation script"""
    print("🔍 ReadyGary Exhaustive Beam Search Baseline")
    print("=" * 50)
    
    # Generate realistic TDL channels
    print("📡 Generating realistic TDL channels...")
    channels = generate_tdl_channels(num_channels=1000)
    print(f"✅ Generated {len(channels)} channels")
    
    # Initialize exhaustive search
    searcher = ExhaustiveBeamSearch(num_tx_beams=64, num_rx_beams=64)
    
    # Run evaluation
    print("🔍 Running exhaustive search...")
    results = searcher.evaluate_performance(channels)
    
    # Print results
    print(f"\n📊 Results:")
    print(f"   Average SNR: {results['avg_snr']:.2f} dB")
    print(f"   Average search time: {results['avg_search_time']*1000:.2f} ms")
    print(f"   Total evaluation time: {results['total_time']:.2f} s")
    
    # Plot results
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.hist(results['snr_values'], bins=50, alpha=0.7)
    plt.xlabel('SNR (dB)')
    plt.ylabel('Frequency')
    plt.title('SNR Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    plt.hist(results['search_times'], bins=50, alpha=0.7)
    plt.xlabel('Search Time (s)')
    plt.ylabel('Frequency')
    plt.title('Search Time Distribution')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 3)
    tx_beams = [pair[0] for pair in results['beam_pairs']]
    rx_beams = [pair[1] for pair in results['beam_pairs']]
    plt.scatter(tx_beams, rx_beams, alpha=0.6)
    plt.xlabel('TX Beam Index')
    plt.ylabel('RX Beam Index')
    plt.title('Optimal Beam Pairs')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('docs/figs/exhaustive_search_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n✅ Results saved to docs/figs/exhaustive_search_results.png")

if __name__ == "__main__":
    main()
EOF'
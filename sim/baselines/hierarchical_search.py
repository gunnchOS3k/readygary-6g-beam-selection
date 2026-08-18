"""
Hierarchical Beam Search
More efficient than exhaustive search, but still comprehensive
"""
import numpy as np
import time
from typing import Tuple, List, Dict
from exhaustive_search import ExhaustiveBeamSearch

class HierarchicalBeamSearch:
    """
    Hierarchical search: coarse -> fine beam refinement
    Addresses efficiency while maintaining good performance
    """
    
    def __init__(self, num_tx_beams: int = 64, num_rx_beams: int = 64):
        self.num_tx_beams = num_tx_beams
        self.num_rx_beams = num_rx_beams
        self.search_time = 0.0
        
    def generate_codebook(self, num_beams: int, num_antennas: int = 8) -> np.ndarray:
        """Generate DFT codebook for beamforming"""
        codebook = np.zeros((num_beams, num_antennas), dtype=complex)
        for i in range(num_beams):
            for j in range(num_antennas):
                codebook[i, j] = np.exp(1j * 2 * np.pi * i * j / num_beams)
        return codebook / np.sqrt(num_antennas)
    
    def compute_snr(self, H: np.ndarray, tx_beam: np.ndarray, rx_beam: np.ndarray) -> float:
        """Compute SNR for given channel and beam pair"""
        tx_signal = tx_beam @ H @ rx_beam
        snr = np.abs(tx_signal) ** 2
        return snr
    
    def coarse_search(self, H: np.ndarray, coarse_factor: int = 4) -> Tuple[int, int, float]:
        """Coarse search with reduced beam resolution"""
        start_time = time.time()
        
        # Generate coarse codebooks
        coarse_tx_beams = self.num_tx_beams // coarse_factor
        coarse_rx_beams = self.num_rx_beams // coarse_factor
        
        tx_codebook = self.generate_codebook(coarse_tx_beams)
        rx_codebook = self.generate_codebook(coarse_rx_beams)
        
        max_snr = 0.0
        best_tx_idx = 0
        best_rx_idx = 0
        
        # Coarse search
        for tx_idx in range(coarse_tx_beams):
            for rx_idx in range(coarse_rx_beams):
                snr = self.compute_snr(H, tx_codebook[tx_idx], rx_codebook[rx_idx])
                if snr > max_snr:
                    max_snr = snr
                    best_tx_idx = tx_idx
                    best_rx_idx = rx_idx
        
        search_time = time.time() - start_time
        return best_tx_idx, best_rx_idx, max_snr, search_time
    
    def fine_search(self, H: np.ndarray, coarse_tx: int, coarse_rx: int, 
                   search_window: int = 8) -> Tuple[int, int, float]:
        """Fine search around coarse solution"""
        start_time = time.time()
        
        # Generate full resolution codebooks
        tx_codebook = self.generate_codebook(self.num_tx_beams)
        rx_codebook = self.generate_codebook(self.num_rx_beams)
        
        # Define search window around coarse solution
        tx_start = max(0, coarse_tx * 4 - search_window)
        tx_end = min(self.num_tx_beams, coarse_tx * 4 + search_window)
        rx_start = max(0, coarse_rx * 4 - search_window)
        rx_end = min(self.num_rx_beams, coarse_rx * 4 + search_window)
        
        max_snr = 0.0
        best_tx_idx = coarse_tx * 4
        best_rx_idx = coarse_rx * 4
        
        # Fine search
        for tx_idx in range(tx_start, tx_end):
            for rx_idx in range(rx_start, rx_end):
                snr = self.compute_snr(H, tx_codebook[tx_idx], rx_codebook[rx_idx])
                if snr > max_snr:
                    max_snr = snr
                    best_tx_idx = tx_idx
                    best_rx_idx = rx_idx
        
        search_time = time.time() - start_time
        return best_tx_idx, best_rx_idx, max_snr, search_time
    
    def search_optimal_beams(self, H: np.ndarray) -> Tuple[int, int, float, float]:
        """Hierarchical search: coarse -> fine"""
        # Step 1: Coarse search
        coarse_tx, coarse_rx, coarse_snr, coarse_time = self.coarse_search(H)
        
        # Step 2: Fine search around coarse solution
        fine_tx, fine_rx, fine_snr, fine_time = self.fine_search(H, coarse_tx, coarse_rx)
        
        total_time = coarse_time + fine_time
        self.search_time = total_time
        
        return fine_tx, fine_rx, fine_snr, total_time
    
    def evaluate_performance(self, channels: List[np.ndarray]) -> Dict:
        """Evaluate hierarchical search performance"""
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

def compare_baselines():
    """Compare exhaustive vs hierarchical search"""
    print("🔍 ReadyGary Baseline Comparison")
    print("=" * 50)
    
    # Generate test channels
    from exhaustive_search import generate_tdl_channels
    channels = generate_tdl_channels(num_channels=100)
    
    # Exhaustive search
    print("📊 Running exhaustive search...")
    exhaustive_searcher = ExhaustiveBeamSearch()
    exhaustive_results = exhaustive_searcher.evaluate_performance(channels)
    
    # Hierarchical search
    print("📊 Running hierarchical search...")
    hierarchical_searcher = HierarchicalBeamSearch()
    hierarchical_results = hierarchical_searcher.evaluate_performance(channels)
    
    # Compare results
    print(f"\n📈 Comparison Results:")
    print(f"   Exhaustive - Avg SNR: {exhaustive_results['avg_snr']:.2f} dB")
    print(f"   Exhaustive - Avg Time: {exhaustive_results['avg_search_time']*1000:.2f} ms")
    print(f"   Hierarchical - Avg SNR: {hierarchical_results['avg_snr']:.2f} dB")
    print(f"   Hierarchical - Avg Time: {hierarchical_results['avg_search_time']*1000:.2f} ms")
    
    # Calculate efficiency
    snr_loss = exhaustive_results['avg_snr'] - hierarchical_results['avg_snr']
    time_speedup = exhaustive_results['avg_search_time'] / hierarchical_results['avg_search_time']
    
    print(f"\n⚡ Efficiency Metrics:")
    print(f"   SNR Loss: {snr_loss:.2f} dB")
    print(f"   Time Speedup: {time_speedup:.2f}x")
    
    return exhaustive_results, hierarchical_results

if __name__ == "__main__":
    compare_baselines()

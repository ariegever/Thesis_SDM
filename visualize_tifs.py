import os
import numpy as np
import matplotlib.pyplot as plt
import tifffile

def visualize_all_tifs():
    folder = r"c:\Users\ADMIN\Desktop\Thesis\Thesis_SDM"
    files = [f for f in os.listdir(folder) if f.endswith('.tif') and 'avocado' in f]
    
    if not files:
        print("No avocado .tif files found.")
        return

    # Sort files to have Current first, then chronologically
    # Custom sort logic
    def sort_key(name):
        if 'current' in name: return 0
        if '2050' in name: return 1
        if '2100' in name: return 2
        return 3
    
    files.sort(key=sort_key)
    
    num_files = len(files)
    cols = 3
    rows = (num_files + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()
    
    # Common settings
    cmap = 'RdYlGn'  # Red-Yellow-Green (Low to High Suitability)
    vmin = 0.0
    vmax = 1.0
    
    print(f"Plotting {num_files} maps with fixed scale (0 to 1)...")
    
    # Load Current Map first to create mask
    current_file = [f for f in files if 'current' in f][0]
    current_path = os.path.join(folder, current_file)
    try:
        current_data = tifffile.imread(current_path)
        # Create mask: Valid if not NaN and not 0 (assuming 0 is background/sea)
        # Adjust threshold if needed (e.g. > 0.001)
        valid_mask = (current_data > 0) & (~np.isnan(current_data))
        print(f"Created mask from {current_file}. Valid pixels: {np.sum(valid_mask)}")
    except Exception as e:
        print(f"Error loading mask from {current_file}: {e}")
        valid_mask = None

    for i, filename in enumerate(files):
        filepath = os.path.join(folder, filename)
        ax = axes[i]
        
        try:
            data = tifffile.imread(filepath)
            
            # Apply Mask
            if valid_mask is not None:
                # Ensure shapes match
                if data.shape == valid_mask.shape:
                    data = np.where(valid_mask, data, np.nan)
                else:
                    print(f"Shape mismatch for {filename}: {data.shape} vs {valid_mask.shape}")

            im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
            ax.set_title(filename.replace('.tif', ''), fontsize=10)
            ax.axis('off')
            
            # Add stats text
            valid_data = data[~np.isnan(data)]
            if len(valid_data) > 0:
                mean_val = np.mean(valid_data)
                max_val = np.max(valid_data)
                ax.text(0.05, 0.05, f"Max: {max_val:.2f}\nMean: {mean_val:.2f}", 
                        transform=ax.transAxes, color='black', fontsize=8,
                        bbox=dict(facecolor='white', alpha=0.7))
            else:
                 ax.text(0.5, 0.5, "No Valid Data", ha='center')
            
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            ax.text(0.5, 0.5, "Error", ha='center')

    # Hide empty subplots
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    # Add colorbar
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax)), cax=cbar_ax)
    cbar_ax.set_ylabel('Suitability Probability', rotation=270, labelpad=15)

    plt.suptitle("Avocado Suitability Comparison (Fixed Scale 0-1)", fontsize=16)
    
    output_path = os.path.join(folder, "avocado_suitability_comparison.png")
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved comparison map to: {output_path}")

if __name__ == "__main__":
    visualize_all_tifs()

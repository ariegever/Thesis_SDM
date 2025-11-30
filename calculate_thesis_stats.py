import os
import numpy as np
import pandas as pd
import tifffile

def calculate_stats():
    folder = r"c:\Users\ADMIN\Desktop\Thesis\Thesis_SDM"
    files = [f for f in os.listdir(folder) if f.endswith('.tif') and 'avocado' in f]
    
    # Sort: Current, then 2050s, then 2100s
    def sort_key(name):
        if 'current' in name: return 0
        if '2050' in name: return 1 if 'ssp245' in name else 2
        if '2100' in name: return 3 if 'ssp245' in name else 4
        return 5
    files.sort(key=sort_key)
    
    # Load mask from current
    current_file = [f for f in files if 'current' in f][0]
    current_data = tifffile.imread(os.path.join(folder, current_file))
    valid_mask = (current_data > 0) & (~np.isnan(current_data))
    total_pixels = np.sum(valid_mask)
    
    results = []
    
    for filename in files:
        filepath = os.path.join(folder, filename)
        data = tifffile.imread(filepath)
        
        # Apply mask
        valid_data = data[valid_mask]
        
        # Metrics
        mean_val = np.mean(valid_data)
        max_val = np.max(valid_data)
        
        # Thresholds
        area_mod = np.sum(valid_data > 0.5)
        area_high = np.sum(valid_data > 0.7)
        
        pct_mod = (area_mod / total_pixels) * 100
        pct_high = (area_high / total_pixels) * 100
        
        results.append({
            "Scenario": filename.replace('avocado_', '').replace('.tif', ''),
            "Mean Suitability": mean_val,
            "Max Suitability": max_val,
            "% Area > 0.5": pct_mod,
            "% Area > 0.7": pct_high
        })
        
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Calculate Changes relative to Current
    current_row = df.iloc[0]
    df['Mean Change (%)'] = ((df['Mean Suitability'] - current_row['Mean Suitability']) / current_row['Mean Suitability']) * 100
    df['High Area Change (%)'] = ((df['% Area > 0.7'] - current_row['% Area > 0.7']) / current_row['% Area > 0.7']) * 100
    
    # Handle divide by zero if current area is 0 (unlikely but safe)
    df = df.fillna(0)

    print(df.to_markdown(index=False, floatfmt=".2f"))
    
    # Save to CSV
    df.to_csv(os.path.join(folder, "thesis_stats.csv"), index=False)
    print(f"\nSaved stats to {os.path.join(folder, 'thesis_stats.csv')}")

if __name__ == "__main__":
    calculate_stats()

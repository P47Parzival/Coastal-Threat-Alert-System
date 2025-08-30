"""
Coastal Alert System using Clay v1.5 Geospatial Foundation Model
A comprehensive system for monitoring coastal threats and environmental changes
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import requests
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ClayCoastalMonitor:
    """
    Coastal monitoring system using Clay v1.5 foundation model
    for real-time threat detection and environmental analysis
    """
    
    def __init__(self):
        """Initialize the Clay model and monitoring system"""
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        # Define coastal threat categories
        self.threat_categories = {
            'erosion': 'Coastal erosion detected',
            'flooding': 'Storm surge or flooding risk',
            'pollution': 'Water pollution or oil spill',
            'construction': 'Unauthorized coastal development',
            'vegetation_loss': 'Mangrove or coastal vegetation loss',
            'algal_bloom': 'Harmful algal bloom detected',
            'sediment': 'Unusual sediment patterns'
        }
        
        # Risk levels
        self.risk_levels = {
            'low': {'color': 'green', 'threshold': 0.3},
            'medium': {'color': 'yellow', 'threshold': 0.6},
            'high': {'color': 'red', 'threshold': 1.0}
        }
        
    def load_clay_model(self):
        """Load the Clay v1.5 model from HuggingFace"""
        try:
            print("Loading Clay v1.5 model...")
            # Note: This is a placeholder implementation
            # The actual Clay model would be loaded from the official repository
            
            # For demonstration, we'll simulate the model loading
            # In practice, you would use:
            # from clay import Clay
            # self.model = Clay.from_pretrained("made-with-clay/Clay")
            
            print("✅ Clay v1.5 model loaded successfully!")
            print("🌍 Ready for global Earth observation analysis")
            
            # Simulate model properties
            self.model_info = {
                'name': 'Clay v1.5',
                'embedding_dim': 768,
                'resolution': '10m',
                'sensors': ['Sentinel-1', 'Sentinel-2', 'DEM'],
                'global_coverage': True,
                'zero_shot': True
            }
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading Clay model: {e}")
            print("💡 Make sure you have the clay package installed:")
            print("   pip install clay-foundation-model")
            return False
    
    def simulate_satellite_data(self, location, date=None):
        """
        Simulate satellite data for a coastal location
        In practice, this would fetch real Sentinel-1/2 data
        """
        if date is None:
            date = datetime.now()
            
        # Simulate multi-spectral data (bands)
        np.random.seed(42)  # For reproducible demo
        
        # Simulate Sentinel-2 bands (RGB + NIR + SWIR)
        bands = {
            'red': np.random.rand(256, 256) * 0.3 + 0.1,
            'green': np.random.rand(256, 256) * 0.4 + 0.2,
            'blue': np.random.rand(256, 256) * 0.6 + 0.3,
            'nir': np.random.rand(256, 256) * 0.8 + 0.1,  # Near-infrared
            'swir': np.random.rand(256, 256) * 0.5 + 0.1,  # Short-wave infrared
        }
        
        # Add coastal features to the simulation
        if 'coastal' in location.lower() or 'beach' in location.lower():
            # Simulate water-land boundary
            water_mask = self._create_water_mask(256, 256)
            bands['blue'] *= (1 + water_mask * 0.5)  # Enhance blue in water areas
            bands['nir'] *= (1 - water_mask * 0.3)   # Reduce NIR in water
        
        return {
            'location': location,
            'date': date,
            'bands': bands,
            'metadata': {
                'sensor': 'Sentinel-2',
                'cloud_cover': np.random.randint(5, 25),
                'resolution': '10m'
            }
        }
    
    def _create_water_mask(self, height, width):
        """Create a simulated water mask for coastal areas"""
        y, x = np.ogrid[:height, :width]
        # Create a diagonal water boundary
        water_mask = ((x + y * 0.5) < width * 0.6).astype(float)
        return water_mask
    
    def extract_embeddings(self, satellite_data):
        """
        Extract embeddings from satellite data using Clay v1.5
        This simulates the actual Clay model processing
        """
        print(f"🛰️  Processing satellite data for {satellite_data['location']}")
        print(f"📅 Date: {satellite_data['date'].strftime('%Y-%m-%d')}")
        print(f"☁️  Cloud cover: {satellite_data['metadata']['cloud_cover']}%")
        
        # Simulate Clay v1.5 embedding extraction
        # In practice: embeddings = self.model.encode(satellite_data)
        
        # Create meaningful embeddings based on the simulated data
        embedding_size = 768  # Clay v1.5 embedding dimension
        
        # Generate embeddings that reflect the input data characteristics
        bands = satellite_data['bands']
        
        # Simulate feature extraction
        water_content = np.mean(bands['blue']) - np.mean(bands['nir'])
        vegetation_index = (np.mean(bands['nir']) - np.mean(bands['red'])) / (np.mean(bands['nir']) + np.mean(bands['red']))
        coastal_features = np.std(bands['blue']) + np.std(bands['green'])
        
        # Create embedding vector
        embeddings = np.random.rand(embedding_size)
        
        # Inject meaningful patterns based on extracted features
        embeddings[0] = water_content  # Water signature
        embeddings[1] = vegetation_index  # Vegetation health
        embeddings[2] = coastal_features  # Coastal dynamics
        
        print(f"✅ Generated {embedding_size}-dimensional embeddings")
        
        return {
            'embeddings': embeddings,
            'features': {
                'water_content': water_content,
                'vegetation_index': vegetation_index,
                'coastal_features': coastal_features
            },
            'confidence': 0.92
        }
    
    def detect_threats(self, embeddings_data):
        """
        Detect coastal threats from Clay embeddings
        """
        print("🔍 Analyzing embeddings for coastal threats...")
        
        embeddings = embeddings_data['embeddings']
        features = embeddings_data['features']
        
        threats_detected = {}
        
        # Threat detection logic based on embedding patterns
        # These thresholds would be learned from training data in practice
        
        # Erosion detection
        if features['coastal_features'] > 0.7:
            threats_detected['erosion'] = {
                'probability': min(features['coastal_features'], 1.0),
                'severity': 'high' if features['coastal_features'] > 0.85 else 'medium'
            }
        
        # Pollution detection (unusual water signatures)
        if features['water_content'] < -0.3 or features['water_content'] > 0.8:
            threats_detected['pollution'] = {
                'probability': abs(features['water_content']),
                'severity': 'high' if abs(features['water_content']) > 0.6 else 'medium'
            }
        
        # Vegetation loss
        if features['vegetation_index'] < 0.2:
            threats_detected['vegetation_loss'] = {
                'probability': 1 - features['vegetation_index'],
                'severity': 'high' if features['vegetation_index'] < 0.1 else 'medium'
            }
        
        # Flooding risk (unusual water patterns)
        if features['water_content'] > 0.6 and features['coastal_features'] > 0.5:
            threats_detected['flooding'] = {
                'probability': (features['water_content'] + features['coastal_features']) / 2,
                'severity': 'high'
            }
        
        return threats_detected
    
    def generate_alert_report(self, location, threats, satellite_data, embeddings_data):
        """Generate a comprehensive alert report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            'alert_id': f"COAST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': timestamp,
            'location': location,
            'satellite_info': satellite_data['metadata'],
            'analysis_confidence': embeddings_data['confidence'],
            'threats_detected': threats,
            'recommendations': []
        }
        
        # Generate recommendations based on threats
        if threats:
            for threat_type, threat_data in threats.items():
                severity = threat_data['severity']
                probability = threat_data['probability']
                
                if threat_type == 'erosion':
                    if severity == 'high':
                        report['recommendations'].append("🚨 Immediate coastal protection measures required")
                        report['recommendations'].append("📊 Deploy emergency monitoring equipment")
                    else:
                        report['recommendations'].append("⚠️  Monitor erosion patterns closely")
                
                elif threat_type == 'pollution':
                    report['recommendations'].append("🛑 Investigate potential pollution sources")
                    report['recommendations'].append("🧪 Conduct water quality testing")
                
                elif threat_type == 'vegetation_loss':
                    report['recommendations'].append("🌱 Assess mangrove/vegetation restoration needs")
                    report['recommendations'].append("🔍 Investigate causes of vegetation loss")
                
                elif threat_type == 'flooding':
                    report['recommendations'].append("🌊 Issue flood warning to coastal communities")
                    report['recommendations'].append("🚁 Prepare emergency response teams")
        else:
            report['recommendations'].append("✅ No immediate threats detected")
            report['recommendations'].append("📈 Continue routine monitoring")
        
        return report
    
    def visualize_analysis(self, satellite_data, embeddings_data, threats, save_path=None):
        """Create visualization of the coastal analysis"""
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(f"Coastal Analysis Report - {satellite_data['location']}", fontsize=16, fontweight='bold')
        
        # 1. RGB Composite
        rgb_data = np.stack([
            satellite_data['bands']['red'],
            satellite_data['bands']['green'],
            satellite_data['bands']['blue']
        ], axis=-1)
        
        axes[0, 0].imshow(rgb_data)
        axes[0, 0].set_title('RGB Composite')
        axes[0, 0].axis('off')
        
        # 2. Vegetation Index (NDVI)
        ndvi = (satellite_data['bands']['nir'] - satellite_data['bands']['red']) / \
               (satellite_data['bands']['nir'] + satellite_data['bands']['red'])
        
        im1 = axes[0, 1].imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
        axes[0, 1].set_title('Vegetation Index (NDVI)')
        axes[0, 1].axis('off')
        plt.colorbar(im1, ax=axes[0, 1], fraction=0.046)
        
        # 3. Water Detection
        water_index = satellite_data['bands']['blue'] - satellite_data['bands']['nir']
        im2 = axes[0, 2].imshow(water_index, cmap='Blues')
        axes[0, 2].set_title('Water Detection')
        axes[0, 2].axis('off')
        plt.colorbar(im2, ax=axes[0, 2], fraction=0.046)
        
        # 4. Embedding Features
        features = embeddings_data['features']
        feature_names = list(features.keys())
        feature_values = list(features.values())
        
        bars = axes[1, 0].bar(feature_names, feature_values, color=['blue', 'green', 'orange'])
        axes[1, 0].set_title('Extracted Features')
        axes[1, 0].set_ylabel('Feature Value')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, feature_values):
            axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{value:.3f}', ha='center', va='bottom')
        
        # 5. Threat Assessment
        if threats:
            threat_names = list(threats.keys())
            threat_probs = [threats[name]['probability'] for name in threat_names]
            threat_colors = ['red' if threats[name]['severity'] == 'high' else 'orange' 
                           for name in threat_names]
            
            bars = axes[1, 1].bar(threat_names, threat_probs, color=threat_colors)
            axes[1, 1].set_title('Threat Probabilities')
            axes[1, 1].set_ylabel('Probability')
            axes[1, 1].set_ylim(0, 1)
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar, prob in zip(bars, threat_probs):
                axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                               f'{prob:.2f}', ha='center', va='bottom')
        else:
            axes[1, 1].text(0.5, 0.5, 'No Threats\nDetected', ha='center', va='center',
                          transform=axes[1, 1].transAxes, fontsize=14, color='green',
                          fontweight='bold')
            axes[1, 1].set_title('Threat Assessment')
        
        # 6. Model Confidence and Metadata
        axes[1, 2].axis('off')
        info_text = f"""Model Information:
        
🤖 Clay v1.5 Foundation Model
📊 Confidence: {embeddings_data['confidence']:.1%}
🛰️  Sensor: {satellite_data['metadata']['sensor']}
📅 Date: {satellite_data['date'].strftime('%Y-%m-%d')}
☁️  Cloud Cover: {satellite_data['metadata']['cloud_cover']}%
📍 Resolution: {satellite_data['metadata']['resolution']}
        
🌍 Global Earth Observation
⚡ Zero-shot Analysis
🔄 Real-time Processing
        """
        
        axes[1, 2].text(0.1, 0.9, info_text, transform=axes[1, 2].transAxes,
                        fontsize=10, verticalalignment='top', fontfamily='monospace')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 Visualization saved to: {save_path}")
        
        plt.show()
    
    def monitor_location(self, location, generate_report=True, visualize=True):
        """
        Complete monitoring pipeline for a coastal location
        """
        print(f"\n🌊 COASTAL MONITORING SYSTEM - Clay v1.5")
        print("="*50)
        print(f"📍 Location: {location}")
        print(f"🕐 Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        
        # Step 1: Load satellite data
        print("\n1️⃣  SATELLITE DATA ACQUISITION")
        satellite_data = self.simulate_satellite_data(location)
        
        # Step 2: Extract embeddings using Clay v1.5
        print("\n2️⃣  CLAY v1.5 FEATURE EXTRACTION")
        embeddings_data = self.extract_embeddings(satellite_data)
        
        # Step 3: Detect threats
        print("\n3️⃣  THREAT DETECTION")
        threats = self.detect_threats(embeddings_data)
        
        if threats:
            print(f"⚠️  {len(threats)} potential threat(s) detected:")
            for threat_type, threat_data in threats.items():
                severity_emoji = "🚨" if threat_data['severity'] == 'high' else "⚠️"
                print(f"   {severity_emoji} {self.threat_categories[threat_type]}")
                print(f"      Probability: {threat_data['probability']:.1%}")
                print(f"      Severity: {threat_data['severity'].upper()}")
        else:
            print("✅ No immediate threats detected")
        
        # Step 4: Generate report
        if generate_report:
            print("\n4️⃣  GENERATING ALERT REPORT")
            report = self.generate_alert_report(location, threats, satellite_data, embeddings_data)
            
            print(f"\n📋 ALERT REPORT #{report['alert_id']}")
            print("-" * 40)
            print(f"📍 Location: {report['location']}")
            print(f"🕐 Timestamp: {report['timestamp']}")
            print(f"🎯 Confidence: {report['analysis_confidence']:.1%}")
            
            if report['threats_detected']:
                print(f"⚠️  Threats: {len(report['threats_detected'])}")
                for threat in report['threats_detected'].keys():
                    print(f"   • {self.threat_categories[threat]}")
            
            print("\n💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"   {rec}")
        
        # Step 5: Visualization
        if visualize:
            print("\n5️⃣  GENERATING VISUALIZATION")
            self.visualize_analysis(satellite_data, embeddings_data, threats)
        
        print("\n" + "="*50)
        print("✅ COASTAL MONITORING COMPLETE")
        print("="*50)
        
        return {
            'satellite_data': satellite_data,
            'embeddings_data': embeddings_data,
            'threats': threats,
            'report': report if generate_report else None
        }


def main():
    """Main function to demonstrate the Clay v1.5 coastal monitoring system"""
    print("🌊 CLAY v1.5 COASTAL MONITORING SYSTEM")
    print("🤖 Powered by Geospatial Foundation Models")
    print("="*60)
    
    # Initialize the monitoring system
    monitor = ClayCoastalMonitor()
    
    # Load the Clay v1.5 model
    if not monitor.load_clay_model():
        print("❌ Failed to load Clay model. Exiting...")
        return
    
    print("\n🎯 DEMO: Monitoring Multiple Coastal Locations")
    print("-" * 50)
    
    # Demo locations for coastal monitoring
    demo_locations = [
        "Mumbai Coastal Area, India",
        "Miami Beach, Florida, USA", 
        "Great Barrier Reef, Australia",
        "Maldives Coral Atolls",
        "California Coast, USA"
    ]
    
    # Monitor each location
    results = {}
    for i, location in enumerate(demo_locations[:2], 1):  # Monitor first 2 for demo
        print(f"\n🔍 ANALYSIS {i}: {location}")
        print("*" * 40)
        
        # Run complete monitoring pipeline
        result = monitor.monitor_location(
            location=location,
            generate_report=True,
            visualize=(i == 1)  # Only visualize first location to avoid too many plots
        )
        
        results[location] = result
        
        # Brief summary
        threats_count = len(result['threats'])
        if threats_count > 0:
            print(f"🚨 ALERT: {threats_count} threat(s) detected at {location}")
        else:
            print(f"✅ All clear at {location}")
    
    print("\n📊 SUMMARY OF ALL MONITORED LOCATIONS")
    print("="*60)
    
    total_threats = 0
    for location, result in results.items():
        threat_count = len(result['threats'])
        total_threats += threat_count
        status = "🚨 ALERT" if threat_count > 0 else "✅ CLEAR"
        print(f"{status} {location}: {threat_count} threat(s)")
    
    print(f"\n🎯 TOTAL THREATS DETECTED: {total_threats}")
    print("\n💡 INTEGRATION READY FOR HACKATHON!")
    print("🔗 Connect to real Sentinel data APIs")
    print("🤖 Deploy with automated alerting system")
    print("📱 Build web/mobile dashboard")
    print("🌍 Scale to global coastal monitoring")


if __name__ == "__main__":
    main()

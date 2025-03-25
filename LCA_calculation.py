#%%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

class SAF_LCA_Model:
    """
    Life Cycle Assessment (LCA) Model for Sustainable Aviation Fuel (SAF)
    """
    
    def __init__(self, pathway="FT", functional_unit="MJ", co2_source=None):
        """
        Initialize the SAF LCA model
        
        Parameters:
        -----------
        pathway : str
            Production pathway (e.g. "FT")
        functional_unit : str
            Functional unit for LCA calculations ("MJ", "kg", "L")
        co2_source : str
            Source of CO2 for pathways that require carbon input (e.g., "DAC", "biogenic", "industrial")
        """
        self.pathway = pathway
        self.functional_unit = functional_unit
        self.co2_source = co2_source
        
        # Default parameters
        self.feedstock_data = {}
        self.conversion_data = {}
        self.distribution_data = {}
        self.use_phase_data = {}
        self.carbon_capture_data = {}
        self.electrolysis_data = {}
        
        # GHG characterization factors (kg CO2e per kg)
        self.ghg_factors = {
            "CO2": 1,
            "CH4": 28,  # GWP100
            "N2O": 265  # GWP100
        }
        
        # Initialize results
        self.results = {
            "ghg_emissions": {},
            "energy_consumption": {},
            "water_usage": {},
            "land_use": {}
        }
    
    def set_feedstock_data(self, feedstock_type, ghg_emissions, energy_input, 
                          water_usage, land_use, yield_rate):
        """
        Set feedstock production stage data
        
        Parameters:
        -----------
        feedstock_type : str
            Type of feedstock (e.g., "used cooking oil", "jatropha", "corn")
        ghg_emissions : float
            GHG emissions from feedstock production (kg CO2e per kg feedstock)
        energy_input : float
            Energy input for feedstock production (MJ per kg feedstock)
        water_usage : float
            Water usage (L per kg feedstock)
        land_use : float
            Land use (m2 per kg feedstock)
        yield_rate : float
            Feedstock yield (kg feedstock per ha)
        """
        self.feedstock_data = {
            "type": feedstock_type,
            "ghg_emissions": ghg_emissions,
            "energy_input": energy_input,
            "water_usage": water_usage,
            "land_use": land_use,
            "yield_rate": yield_rate
        }
    
    def set_conversion_data(self, technology, efficiency, ghg_emissions, 
                           energy_input, water_usage,
                           syngas_requirement=None, co_h2_ratio=None):
        """
        Set conversion process data
        
        Parameters:
        -----------
        technology : str
            Conversion technology
        efficiency : float
            Conversion efficiency (MJ fuel/MJ feedstock)
        ghg_emissions : float
            GHG emissions from conversion (kg CO2e per kg fuel)
        energy_input : float
            Energy input for conversion (MJ per kg fuel)
        water_usage : float
            Water usage (L per kg fuel)
        syngas_requirement : float, optional
            Syngas requirement for FT synthesis (kg syngas per kg fuel)
        co_h2_ratio : float, optional
            CO:H2 ratio for FT synthesis
        """
        self.conversion_data = {
            "technology": technology,
            "efficiency": efficiency,
            "ghg_emissions": ghg_emissions,
            "energy_input": energy_input,
            "water_usage": water_usage
        }
        
        # Add additional parameters for e-fuel pathway if provided
        if syngas_requirement is not None:
            self.conversion_data["syngas_requirement"] = syngas_requirement
        
        if co_h2_ratio is not None:
            self.conversion_data["co_h2_ratio"] = co_h2_ratio
    
    def set_distribution_data(self, transport_distance, transport_mode, 
                             ghg_emissions, energy_input):
        """
        Set distribution stage data
        
        Parameters:
        -----------
        transport_distance : float
            Transport distance (km)
        transport_mode : str
            Transport mode (e.g., "truck", "rail", "ship")
        ghg_emissions : float
            GHG emissions from distribution (kg CO2e per kg fuel)
        energy_input : float
            Energy input for distribution (MJ per kg fuel)
        """
        self.distribution_data = {
            "transport_distance": transport_distance,
            "transport_mode": transport_mode,
            "ghg_emissions": ghg_emissions,
            "energy_input": energy_input
        }
    
    def set_use_phase_data(self, combustion_emissions, energy_density):
        """
        Set use phase data
        
        Parameters:
        -----------
        combustion_emissions : float
            GHG emissions from fuel combustion (kg CO2e per kg fuel)
        energy_density : float
            Energy density of fuel (MJ per kg)
        """
        self.use_phase_data = {
            "combustion_emissions": combustion_emissions,
            "energy_density": energy_density
        }
    
    def set_carbon_capture_data(self, capture_efficiency, energy_requirement, 
                               ghg_emissions, water_usage, co2_capture_rate):
        """
        Set carbon capture data for Direct Air Capture (DAC) or other CO2 sources
        
        Parameters:
        -----------
        capture_efficiency : float
            CO2 capture efficiency (%)
        energy_requirement : float
            Energy input for carbon capture (MJ per kg CO2)
        ghg_emissions : float
            GHG emissions from capture process (kg CO2e per kg CO2 captured)
        water_usage : float
            Water usage (L per kg CO2 captured)
        co2_capture_rate : float
            Amount of CO2 captured and used per kg of fuel produced (kg CO2/kg fuel)
        """
        self.carbon_capture_data = {
            "capture_efficiency": capture_efficiency,
            "energy_requirement": energy_requirement,
            "ghg_emissions": ghg_emissions,
            "water_usage": water_usage,
            "co2_capture_rate": co2_capture_rate
        }
    
    def set_electrolysis_data(self, co2_electrolysis_efficiency, water_electrolysis_efficiency,
                             electricity_source, energy_input_co, energy_input_h2, water_usage,
                             electricity_carbon_intensity=None):
        """
        Set electrolysis data for CO2 to CO conversion and H2 production
        
        Parameters:
        -----------
        co2_electrolysis_efficiency : float
            Efficiency of CO2 to CO conversion (%)
        water_electrolysis_efficiency : float
            Efficiency of water electrolysis for H2 production (%)
        electricity_source : str
            Source of electricity (e.g., "grid", "renewable", "mixed")
        energy_input_co : float
            Energy input for CO2 electrolysis (MJ per kg CO)
        energy_input_h2 : float
            Energy input for water electrolysis (MJ per kg H2)
        water_usage : float
            Water usage for electrolysis (L per kg H2+CO produced)
        electricity_carbon_intensity : float, optional
            Carbon intensity of electricity (kg CO2e/kWh). If None, will be set based on electricity_source.
        """
        # Define carbon intensities for different electricity sources (kg CO2e/kWh)
        electricity_carbon_intensities = {
            "grid_global": 0.475,       # Global average grid electricity
            "grid_eu": 0.253,           # European Union average
            "grid_china": 0.638,        # China average
            "grid_us": 0.389,           # US average
            "natural_gas": 0.410,       # Natural gas combined cycle
            "coal": 0.820,              # Coal power plants
            "solar": 0.048,             # Solar PV
            "wind": 0.011,              # Wind power
            "hydro": 0.024,             # Hydroelectric
            "nuclear": 0.012,           # Nuclear power
            "biomass": 0.230,           # Biomass power
            "renewable_mix": 0.030,     # Mix of solar, wind, and hydro
            "low_carbon_mix": 0.100,    # Mix of renewables and nuclear
            "renewable": 0.020          # Generic renewable (default)
        }
        
        # If electricity_carbon_intensity is not provided, set it based on the source
        if electricity_carbon_intensity is None:
            if electricity_source in electricity_carbon_intensities:
                electricity_carbon_intensity = electricity_carbon_intensities[electricity_source]
            else:
                # Default to renewable if source not recognized
                electricity_carbon_intensity = electricity_carbon_intensities["renewable"]
                print(f"Warning: Electricity source '{electricity_source}' not recognized. Using default value.")
        
        self.electrolysis_data = {
            "co2_electrolysis_efficiency": co2_electrolysis_efficiency,
            "water_electrolysis_efficiency": water_electrolysis_efficiency,
            "electricity_source": electricity_source,
            "electricity_carbon_intensity": electricity_carbon_intensity,
            "energy_input_co": energy_input_co,
            "energy_input_h2": energy_input_h2,
            "water_usage": water_usage
        }
    
    def analyze_electricity_sources(self, electricity_sources=None):
        """
        Analyze the impact of different electricity sources on SAF carbon intensity
        
        Parameters:
        -----------
        electricity_sources : list, optional
            List of electricity sources to analyze. If None, a default set will be used.
            
        Returns:
        --------
        DataFrame: Results of electricity source analysis
        """
        # If no sources provided, use a default set
        if electricity_sources is None:
            electricity_sources = [
                "renewable_mix", "grid_global", "grid_eu", "grid_us", 
                "grid_china", "natural_gas", "coal", "solar", "wind", "hydro", "renewable"
            ]
        
        # Store original parameters to restore later
        original_source = self.electrolysis_data.get("electricity_source", "renewable")
        original_intensity = self.electrolysis_data.get("electricity_carbon_intensity", 0.020)
        original_co = self.electrolysis_data.get("energy_input_co", 28.0)
        original_h2 = self.electrolysis_data.get("energy_input_h2", 55.0)
        
        results = []
        
        # Run analysis for each electricity source
        for source in electricity_sources:
            # Update the electricity source and recalculate
            self.set_electrolysis_data(
                co2_electrolysis_efficiency=self.electrolysis_data["co2_electrolysis_efficiency"],
                water_electrolysis_efficiency=self.electrolysis_data["water_electrolysis_efficiency"],
                electricity_source=source,  # New source
                energy_input_co=original_co,
                energy_input_h2=original_h2,
                water_usage=self.electrolysis_data["water_usage"],
                electricity_carbon_intensity=None  # Use default from source
            )
            
            # Calculate LCA with new parameters
            self.calculate_lca()
            
            # 直接计算减排率而不调用函数
            if self.functional_unit == "MJ":
                saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g
            else:
                energy_density = self.use_phase_data["energy_density"]  # MJ/kg
                saf_emissions = self.results["ghg_emissions"]["total"] * 1000 / energy_density
                
            emission_reduction = (89.0 - saf_emissions) / 89.0 * 100
            
            # Store results
            results.append({
                'electricity_source': source,
                'carbon_intensity': self.electrolysis_data["electricity_carbon_intensity"],
                'saf_emissions_mjbasis': saf_emissions,
                'emission_reduction': emission_reduction,
                'electrolysis_emissions': self.results["ghg_emissions"]["electrolysis"] * 1000 / self.use_phase_data["energy_density"] if self.functional_unit != "MJ" else self.results["ghg_emissions"]["electrolysis"] * 1000,
                'total_emissions': saf_emissions
            })
        
        # Restore original parameters
        self.set_electrolysis_data(
            co2_electrolysis_efficiency=self.electrolysis_data["co2_electrolysis_efficiency"],
            water_electrolysis_efficiency=self.electrolysis_data["water_electrolysis_efficiency"],
            electricity_source=original_source,
            energy_input_co=original_co,
            energy_input_h2=original_h2,
            water_usage=self.electrolysis_data["water_usage"],
            electricity_carbon_intensity=original_intensity
        )
        
        # 重新计算以恢复原始结果
        self.calculate_lca()
        
        # Create DataFrame from results
        df = pd.DataFrame(results)
        
        # Calculate electrolysis contribution to total emissions
        df['electrolysis_contribution'] = df['electrolysis_emissions'] / df['total_emissions'] * 100
        
        return df
    
    def plot_electricity_analysis(self, results_df, plot_type="emissions"):
        """
        Plot the results of electricity source analysis
        
        Parameters:
        -----------
        results_df : DataFrame
            DataFrame from analyze_electricity_sources method
        plot_type : str
            Type of plot: "emissions", "reduction", or "contribution"
        """
        plt.figure(figsize=(12, 6))
        
        if plot_type == "emissions":
            # Sort by emissions
            sorted_df = results_df.sort_values('saf_emissions_mjbasis', ascending=False)
            
            # Create bar plot
            plt.bar(sorted_df['electricity_source'], sorted_df['saf_emissions_mjbasis'], color='darkblue')
            plt.axhline(y=89.0, color='r', linestyle='-', label='Conventional Jet Fuel (89 g CO2e/MJ)')
            
            plt.title('SAF Carbon Intensity by Electricity Source')
            plt.ylabel('Carbon Intensity (g CO2e/MJ)')
            plt.xlabel('Electricity Source')
            plt.xticks(rotation=45)
            plt.legend()
            
        elif plot_type == "reduction":
            # Sort by reduction
            sorted_df = results_df.sort_values('emission_reduction', ascending=True)
            
            # Create bar plot
            bars = plt.bar(sorted_df['electricity_source'], sorted_df['emission_reduction'], color='green')
            
            # Add threshold line for CORSIA (min 10% reduction)
            plt.axhline(y=10, color='orange', linestyle='--', label='CORSIA Minimum (10%)')
            
            # Add threshold line for EU RED II (min 65% reduction)
            plt.axhline(y=65, color='r', linestyle='--', label='EU RED II Target (65%)')
            
            plt.title('GHG Emission Reduction by Electricity Source')
            plt.ylabel('Emission Reduction (%)')
            plt.xlabel('Electricity Source')
            plt.xticks(rotation=45)
            plt.legend()
            
            # Add values on top of bars
            for bar in bars:
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{height:.1f}%', ha='center', va='bottom')
                
        elif plot_type == "contribution":
            # Sort by contribution
            sorted_df = results_df.sort_values('electrolysis_contribution', ascending=False)
            
            # Create stacked bar plot
            plt.bar(sorted_df['electricity_source'], 
                   sorted_df['electrolysis_emissions'], 
                   label='Electrolysis Emissions', color='orange')
            
            plt.bar(sorted_df['electricity_source'], 
                   sorted_df['total_emissions'] - sorted_df['electrolysis_emissions'],
                   bottom=sorted_df['electrolysis_emissions'], 
                   label='Other Process Emissions', color='blue')
            
            plt.title('Contribution of Electrolysis to Total Emissions')
            plt.ylabel('Emissions (g CO2e/MJ)')
            plt.xlabel('Electricity Source')
            plt.xticks(rotation=45)
            plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        return plt
    
    def calculate_lca(self):
        """
        Calculate the full life cycle assessment for DAC → Electrolysis → FT pathway
        """
        # Check if all required data is available
        if not all([self.carbon_capture_data, self.electrolysis_data,
                   self.conversion_data, self.distribution_data, self.use_phase_data]):
            raise ValueError("Missing required data for LCA calculation for DAC → Electrolysis → FT pathway")
        
        # Calculate GHG emissions for each stage (kg CO2e per functional unit)
        energy_density = self.use_phase_data["energy_density"]  # MJ/kg
        
        # Normalize to functional unit
        if self.functional_unit == "MJ":
            normalization_factor = 1 / energy_density
        elif self.functional_unit == "kg":
            normalization_factor = 1
        elif self.functional_unit == "L":
            # Assuming density of ~0.8 kg/L for SAF
            normalization_factor = 0.8
        else:
            raise ValueError(f"Unsupported functional unit: {self.functional_unit}")
        
        # Carbon capture stage (DAC)
        # 考虑捕获效率影响
        actual_co2_needed = self.carbon_capture_data["co2_capture_rate"] / (self.carbon_capture_data["capture_efficiency"] / 100)
        carbon_capture_ghg = self.carbon_capture_data["ghg_emissions"] * actual_co2_needed * normalization_factor
        
        # Electrolysis stage (CO2 to CO and H2O to H2)
        # Convert electricity carbon intensity from kg CO2e/kWh to kg CO2e/MJ
        elec_intensity_mj = self.electrolysis_data["electricity_carbon_intensity"] / 3.6  # 1 kWh = 3.6 MJ
        
        # Calculate CO and H2 production emissions
        co_h2_ratio = self.conversion_data.get("co_h2_ratio", 1.0)  # Default 1:1 if not specified
        total_syngas_needed = self.conversion_data.get("syngas_requirement", 2.5) * normalization_factor
        
        co_needed = total_syngas_needed * (co_h2_ratio / (1 + co_h2_ratio))
        h2_needed = total_syngas_needed * (1 / (1 + co_h2_ratio))
        
        # 考虑电解效率影响
        actual_co_needed = co_needed / (self.electrolysis_data["co2_electrolysis_efficiency"] / 100)
        actual_h2_needed = h2_needed / (self.electrolysis_data["water_electrolysis_efficiency"] / 100)
        
        # 修正的排放计算
        co_emissions = actual_co_needed * self.electrolysis_data["energy_input_co"] * elec_intensity_mj
        h2_emissions = actual_h2_needed * self.electrolysis_data["energy_input_h2"] * elec_intensity_mj
        
        electrolysis_ghg = co_emissions + h2_emissions
        
        # Conversion stage (Fischer-Tropsch)
        conversion_ghg = self.conversion_data["ghg_emissions"] * normalization_factor
        
        # Distribution stage
        distribution_ghg = self.distribution_data["ghg_emissions"] * normalization_factor
        
        # Use phase (assumed to be carbon neutral when CO2 from air is used)
        use_phase_ghg = self.use_phase_data["combustion_emissions"] * normalization_factor
        
        # Total emissions
        total_ghg = carbon_capture_ghg + electrolysis_ghg + conversion_ghg + distribution_ghg + use_phase_ghg
        
        # Store results
        self.results["ghg_emissions"] = {
            "carbon_capture": carbon_capture_ghg,
            "electrolysis": electrolysis_ghg,
            "conversion": conversion_ghg,
            "distribution": distribution_ghg,
            "use_phase": use_phase_ghg,
            "total": total_ghg
        }
        
        # Calculate energy consumption
        # Carbon capture energy
        carbon_capture_energy = (self.carbon_capture_data["energy_requirement"] * actual_co2_needed) * normalization_factor
        
        # Electrolysis energy - 考虑电解效率
        co_energy = actual_co_needed * self.electrolysis_data["energy_input_co"]
        h2_energy = actual_h2_needed * self.electrolysis_data["energy_input_h2"]
        electrolysis_energy = (co_energy + h2_energy) * normalization_factor
        
        # Conversion and distribution energy
        conversion_energy = self.conversion_data["energy_input"] * normalization_factor
        distribution_energy = self.distribution_data["energy_input"] * normalization_factor
        
        # Total energy
        total_energy = carbon_capture_energy + electrolysis_energy + conversion_energy + distribution_energy
        
        self.results["energy_consumption"] = {
            "carbon_capture": carbon_capture_energy,
            "electrolysis": electrolysis_energy,
            "conversion": conversion_energy,
            "distribution": distribution_energy,
            "total": total_energy
        }
        
        # Calculate water usage
        carbon_capture_water = self.carbon_capture_data["water_usage"] * actual_co2_needed * normalization_factor
        electrolysis_water = self.electrolysis_data["water_usage"] * total_syngas_needed
        conversion_water = self.conversion_data["water_usage"] * normalization_factor
        
        self.results["water_usage"] = {
            "carbon_capture": carbon_capture_water,
            "electrolysis": electrolysis_water,
            "conversion": conversion_water,
            "total": carbon_capture_water + electrolysis_water + conversion_water
        }
        
        # No land use for e-fuel pathway
        self.results["land_use"] = {
            "total": 0
        }
        
        return self.results
    
    def calculate_emission_reduction(self, fossil_jet_emissions=89.0):
        """
        Calculate emission reduction compared to conventional jet fuel
        
        Parameters:
        -----------
        fossil_jet_emissions : float
            Life cycle GHG emissions of fossil jet fuel (g CO2e/MJ)
            Default value is 89.0 g CO2e/MJ based on EU RED II
            
        Returns:
        --------
        float: Emission reduction percentage
        """
        if not self.results["ghg_emissions"]:
            self.calculate_lca()
            
        # Convert results to g CO2e/MJ for comparison if needed
        if self.functional_unit == "MJ":
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g
        else:
            energy_density = self.use_phase_data["energy_density"]  # MJ/kg
            saf_emissions = self.results["ghg_emissions"]["total"] * 1000 / energy_density
            
        reduction = (fossil_jet_emissions - saf_emissions) / fossil_jet_emissions * 100
        return reduction
    
    def plot_results(self, plot_type="emissions_breakdown"):
        """
        Plot LCA results
        
        Parameters:
        -----------
        plot_type : str
            Type of plot to generate
        """
        plt.figure(figsize=(10, 6))
        
        if plot_type == "emissions_breakdown":
            # Emissions breakdown by life cycle stage
            emissions = self.results["ghg_emissions"]
            stages = [k for k in emissions.keys() if k != "total"]
            values = [emissions[k] for k in stages]
            
            plt.bar(stages, values)
            plt.title(f"GHG Emissions Breakdown for {self.pathway} SAF")
            plt.ylabel(f"GHG Emissions (kg CO2e/{self.functional_unit})")
            plt.xticks(rotation=45)
            
        elif plot_type == "energy_breakdown":
            # Energy consumption breakdown
            energy = self.results["energy_consumption"]
            stages = [k for k in energy.keys() if k != "total"]
            values = [energy[k] for k in stages]
            
            plt.bar(stages, values)
            plt.title(f"Energy Consumption Breakdown for {self.pathway} SAF")
            plt.ylabel(f"Energy Consumption (MJ/{self.functional_unit})")
            plt.xticks(rotation=45)
            
        elif plot_type == "comparison":
            # Comparison with fossil jet fuel
            fossil_jet_emissions = 89.0  # g CO2e/MJ
            
            if self.functional_unit == "MJ":
                saf_emissions = self.results["ghg_emissions"]["total"] * 1000  # kg to g
            else:
                energy_density = self.use_phase_data["energy_density"]  # MJ/kg
                saf_emissions = self.results["ghg_emissions"]["total"] * 1000 / energy_density
            
            # 直接计算减排率而不调用函数（避免重复打印）
            reduction_pct = (fossil_jet_emissions - saf_emissions) / fossil_jet_emissions * 100
            
            emissions = [89.0, saf_emissions]  # Fossil jet vs SAF
            plt.bar(["Fossil Jet Fuel", f"{self.pathway} SAF"], emissions)
            plt.title(f"Emissions Comparison: {reduction_pct:.1f}% Reduction")
            plt.ylabel("GHG Emissions (g CO2e/MJ)")
            
        plt.tight_layout()
        plt.show()


# Example usage
if __name__ == "__main__":
    # Create SAF LCA model instance for FT pathway with DAC as CO2 source
    model = SAF_LCA_Model(pathway="FT", functional_unit="MJ", co2_source="DAC")
    
    # Set data for each life cycle stage for e-fuel pathway
    # Values are illustrative and should be replaced with actual data
    
    # Use phase (carbon neutral if CO2 from air)
    model.set_use_phase_data(
        combustion_emissions=0.0,  # kg CO2e/kg fuel (carbon neutral with DAC)
        energy_density=43.0        # MJ/kg fuel (更新为C₁₂H₂₆的能量密度)
    )

    # Carbon capture: Direct Air Capture (DAC)
    # 12 mol CO2 needed per mol C₁₂H₂₆
    # 12 mol CO2 * 44 g/mol = 528 g CO2 per 170.33 g fuel
    # = 3.1 kg CO2/kg fuel
    model.set_carbon_capture_data(
        capture_efficiency=80.0,    # %
        energy_requirement=30.0,    # MJ/kg CO2
        ghg_emissions=0.08,         # kg CO2e/kg CO2 captured (使用绿电)
        water_usage=5.0,            # L/kg CO2 captured
        co2_capture_rate=3.1        # kg CO2/kg fuel (基于C₁₂H₂₆计算)
    )
    
    # Electrolysis for CO2 to CO and H2O to H2
    model.set_electrolysis_data(
        co2_electrolysis_efficiency=65.0,  # % (AEM技术典型效率)
        water_electrolysis_efficiency=75.0, # %
        electricity_source="renewable",     # 使用可再生电力
        energy_input_co=28.0,              # MJ/kg CO (AEM技术能耗更低)
        energy_input_h2=55.0,              # MJ/kg H2
        water_usage=20.0,                  # L/kg H2+CO produced
        electricity_carbon_intensity=None
    )
    
    # Conversion process: Fischer-Tropsch
    # 计算合成气需求：
    # 每摩尔C₁₂H₂₆需要12摩尔CO和13摩尔H2
    # CO: 12 mol * 28 g/mol = 336 g CO
    # H2: 13 mol * 2 g/mol = 26 g H2
    # 总合成气 = 362 g per 170.33 g fuel = 2.13 kg syngas/kg fuel
    model.set_conversion_data(
        technology="Fischer-Tropsch",
        efficiency=0.65,          # MJ fuel/MJ feedstock，暂时没用
        ghg_emissions=0.2,        # kg CO2e/kg fuel
        energy_input=25.0,        # MJ/kg fuel
        water_usage=5.0,          # L/kg fuel
        syngas_requirement=2.13,  # kg syngas/kg fuel (基于C₁₂H₂₆计算)
        co_h2_ratio=0.923        # CO:H2 ratio (12:13 基于C₁₂H₂₆计算)
    )
    
    # Distribution
    model.set_distribution_data(
        transport_distance=500.0,  # km
        transport_mode="truck",
        ghg_emissions=0.05,       # kg CO2e/kg fuel
        energy_input=2.0          # MJ/kg fuel (更新为更实际的值)
    )
    
    # Calculate LCA
    results = model.calculate_lca()
    
    # Calculate emission reduction compared to fossil jet fuel
    reduction = model.calculate_emission_reduction()
    
    # 1. 打印各阶段温室气体排放
    print("\nGHG Emissions Breakdown (g CO2e/MJ):")
    for stage, value in results["ghg_emissions"].items():
        print(f"  {stage}: {value*1000:.2f}")
    
    # 2. 打印各阶段能量消耗
    print("\nEnergy Consumption Breakdown (MJ/functional_unit):")
    for stage, value in results["energy_consumption"].items():
        print(f"  {stage}: {value:.2f}")
    
    # 3. 打印各阶段水资源使用
    print("\nWater Usage Breakdown (L/functional_unit):")
    for stage, value in results["water_usage"].items():
        print(f"  {stage}: {value:.2f}")
    
    # 5. 打印能源效率分析
    print("\nEnergy Efficiency Analysis:")
    print(f"  DAC Energy Share: {(results['energy_consumption']['carbon_capture']/results['energy_consumption']['total']*100):.1f}%")
    print(f"  Electrolysis Energy Share: {(results['energy_consumption']['electrolysis']/results['energy_consumption']['total']*100):.1f}%")
    print(f"  FT Synthesis Energy Share: {(results['energy_consumption']['conversion']/results['energy_consumption']['total']*100):.1f}%")
    
    # Analyze the impact of different electricity sources
    electricity_analysis = model.analyze_electricity_sources()
    
    # Plot the results
    model.plot_electricity_analysis(electricity_analysis, plot_type="emissions")
    model.plot_electricity_analysis(electricity_analysis, plot_type="reduction")
    model.plot_electricity_analysis(electricity_analysis, plot_type="contribution")
    
    # Plot results
    model.plot_results(plot_type="emissions_breakdown")
    model.plot_results(plot_type="comparison")
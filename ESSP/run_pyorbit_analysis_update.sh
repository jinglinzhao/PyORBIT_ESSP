#!/bin/bash

# Flexible PyORBIT YAML Generator and Analysis Runner
# Usage: ./run_pyorbit_analysis.sh [OPTIONS] [INSTRUMENT1] [INSTRUMENT2] ...
# Example: ./run_pyorbit_analysis.sh HARPS HARPSN
# Example: ./run_pyorbit_analysis.sh --indicators BIS,FWHM,H_ALPHA HARPS
# Example: ./run_pyorbit_analysis.sh --indicators FIESTA1 all_instruments

# Default indicators
DEFAULT_INDICATORS=("BIS" "FIESTA1")

# Available instruments list
AVAILABLE_INSTRUMENTS=("HARPS" "HARPSN" "EXPRES" "NEID" "HIRES" "CARMENES" "SOPHIE")

# Function to show usage
show_usage() {
  echo "🚀 PyORBIT YAML Generator and Analysis Runner"
  echo ""
  echo "Usage: $0 [OPTIONS] [INSTRUMENT1] [INSTRUMENT2] ..."
  echo ""
  echo "Options:"
  echo "  --indicators, -i    Comma-separated list of indicators (default: BIS,FIESTA1)"
  echo "  --help, -h          Show this help message"
  echo ""
  echo "Available Instruments:"
  printf "  %s\n" "${AVAILABLE_INSTRUMENTS[@]}"
  echo ""
  echo "Available Indicators:"
  echo "  BIS, FIESTA1, FWHM, H_ALPHA, CCF_FWHM, CONTRAST, RHK"
  echo ""
  echo "Examples:"
  echo "  $0 HARPS HARPSN"
  echo "  $0 --indicators BIS,FWHM HARPS"
  echo "  $0 --indicators FIESTA1 HARPS HARPSN EXPRES NEID"
  echo ""
}

# Function to parse command line arguments
parse_arguments() {
  INDICATORS=("${DEFAULT_INDICATORS[@]}")
  INSTRUMENTS=()
  
  while [[ $# -gt 0 ]]; do
      case $1 in
          --indicators|-i)
              if [[ -n "$2" && "$2" != --* ]]; then
                  IFS=',' read -ra INDICATORS <<< "$2"
                  shift 2
              else
                  echo "❌ Error: --indicators requires a comma-separated list"
                  echo "   Example: --indicators BIS,FWHM,H_ALPHA"
                  exit 1
              fi
              ;;
          --help|-h)
              show_usage
              exit 0
              ;;
          --*)
              echo "❌ Unknown option: $1"
              show_usage
              exit 1
              ;;
          *)
              INSTRUMENTS+=("$1")
              shift
              ;;
      esac
  done
  
  # Validate that we have instruments
  if [ ${#INSTRUMENTS[@]} -eq 0 ]; then
      echo "❌ No instruments specified!"
      echo ""
      show_usage
      exit 1
  fi
}

# Function to get indicator kind (data type)
get_indicator_kind() {
  local indicator="$1"
  
  case "$indicator" in
      "BIS")
          echo "BIS"
          ;;
      "FIESTA1"|"FWHM")
          echo "FWHM"
          ;;
      "H_ALPHA"|"HALPHA")
          echo "H_ALPHA"
          ;;
      "CCF_FWHM")
          echo "FWHM"
          ;;
      "CONTRAST")
          echo "CONTRAST"
          ;;
      "RHK")
          echo "RHK"
          ;;
      *)
          # Default to the indicator name itself
          echo "$indicator"
          ;;
  esac
}

# Function to get derivative setting based on position and total count
get_derivative_setting() {
  local indicator_index="$1"
  local total_indicators="$2"
  
  if [ "$total_indicators" -eq 1 ]; then
      # If only one indicator, it gets derivative
      echo "true"
  elif [ "$total_indicators" -eq 2 ]; then
      # If two indicators, first gets derivative, second doesn't
      if [ "$indicator_index" -eq 0 ]; then
          echo "true"
      else
          echo "false"
      fi
  else
      # If more than two indicators, only first gets derivative
      if [ "$indicator_index" -eq 0 ]; then
          echo "true"
      else
          echo "false"
      fi
  fi
}

# Function to get rot_amp setting based on position and total count
get_rot_amp_setting() {
  local indicator_index="$1"
  local total_indicators="$2"
  
  if [ "$total_indicators" -eq 1 ]; then
      # If only one indicator, it gets rot_amp
      echo "true"
  else
      # If multiple indicators, only first gets rot_amp
      if [ "$indicator_index" -eq 0 ]; then
          echo "true"
      else
          echo "false"
      fi
  fi
}

# Function to get rot_amp boundary values based on position
get_rot_amp_boundary() {
  local instrument_index="$1"
  
  if [ "$instrument_index" -eq 0 ]; then
      # First instrument gets [0.0, 10.0]
      echo "[0.0, 50.0]"
  else
      # All other instruments get [-10.0, 10.0]
      echo "[-50.0, 50.0]"
  fi
}

# Function to generate YAML configuration
generate_yaml_config() {
  local instruments=("$@")
  local indicators_copy=("${INDICATORS[@]}")
  
  # Create filename based on instruments
  if [ ${#instruments[@]} -eq 1 ]; then
      local filename="ESSP_gp_${instruments[0]}.yaml"
      local output_dir="ESSP_gp_${instruments[0]}"
  else
      local combined_instruments=$(IFS=_; echo "${instruments[*]}")
      local filename="ESSP_gp_${combined_instruments}.yaml"
      local output_dir="ESSP_gp_${combined_instruments}"
  fi
  
  echo "📝 Generating configuration file: ${filename}"
  echo "   Instruments: ${instruments[*]}"
  echo "   Indicators: ${indicators_copy[*]}"
  
  # Start generating YAML file
  echo "inputs:" > "${filename}"
  
  # Add RV inputs for each instrument
  for instrument in "${instruments[@]}"; do
      echo "  ESSP_${instrument}:" >> "${filename}"
      echo "    file: ESSP_${instrument}.dat" >> "${filename}"
      echo "    kind: RV" >> "${filename}"
      echo "    models:" >> "${filename}"
      echo "      - radial_velocities" >> "${filename}"
      echo "      - gp_multidimensional" >> "${filename}"
  done
  
  # Add indicator inputs for each instrument
  for instrument in "${instruments[@]}"; do
      for indicator in "${indicators_copy[@]}"; do
          local kind=$(get_indicator_kind "$indicator")
          echo "  ESSP_${indicator}_${instrument}:" >> "${filename}"
          echo "    file: ESSP_${indicator}_${instrument}.dat" >> "${filename}"
          echo "    kind: ${kind}" >> "${filename}"
          echo "    models:" >> "${filename}"
          echo "      - gp_multidimensional" >> "${filename}"
      done
  done
  
  # Add common section
  echo "common:" >> "${filename}"
  echo "  planets:" >> "${filename}"
  echo "    b:" >> "${filename}"
  echo "      orbit: keplerian" >> "${filename}"
  echo "      parametrization: Eastman2013" >> "${filename}"
  echo "      boundaries:" >> "${filename}"
  echo "        P: [1.5, 10.0]" >> "${filename}"
  echo "        K: [0.1, 4.0]" >> "${filename}"
  echo "        e: [0.00, 0.50]" >> "${filename}"
  echo "      priors:" >> "${filename}"
  echo "        P: ['Gaussian', 2.9, 1.0]" >> "${filename}"
  echo "  activity:" >> "${filename}"
  echo "    boundaries:" >> "${filename}"
  echo "      Prot: [20.0, 35.0]" >> "${filename}"
  echo "      Pdec: [10.0, 2000.0]" >> "${filename}"
  echo "      Oamp: [0.01, 5.0]" >> "${filename}"
  echo "    priors:" >> "${filename}"
  echo "      Prot: ['Gaussian', 28.0, 5.0]" >> "${filename}"
  echo "  star:" >> "${filename}"
  echo "    star_parameters:" >> "${filename}"
  echo "      priors:" >> "${filename}"
  echo "        mass: ['Gaussian', 1.0, 1e-10]" >> "${filename}"
  
  # Add models section
  echo "models:" >> "${filename}"
  echo "  radial_velocities:" >> "${filename}"
  echo "    planets:" >> "${filename}"
  echo "      - b" >> "${filename}"
  echo "  polynomial_trend:" >> "${filename}"
  echo "    model: local_polynomial_trend" >> "${filename}"
  echo "    order: 2" >> "${filename}"
  echo "  gp_multidimensional:" >> "${filename}"
  echo "    model: spleaf_multidimensional_esp" >> "${filename}"
  echo "    common: activity" >> "${filename}"
  echo "    n_harmonics: 4" >> "${filename}"
  echo "    hyperparameters_condition: true" >> "${filename}"
  echo "    rotation_decay_condition: true" >> "${filename}"
  echo "    derivative:" >> "${filename}"
  
  # Add derivative settings for RV datasets
  for instrument in "${instruments[@]}"; do
      echo "      ESSP_${instrument}: true" >> "${filename}"
  done
  
  # Add derivative settings for indicators
  for instrument in "${instruments[@]}"; do
      for i in "${!indicators_copy[@]}"; do
          local indicator="${indicators_copy[$i]}"
          local derivative_setting=$(get_derivative_setting "$i" "${#indicators_copy[@]}")
          echo "      ESSP_${indicator}_${instrument}: ${derivative_setting}" >> "${filename}"
      done
  done
  
  # Add GP boundaries sections for RV datasets
  for i in "${!instruments[@]}"; do
      local instrument="${instruments[$i]}"
      local rot_amp_boundary=$(get_rot_amp_boundary "$i")
      echo "    ESSP_${instrument}:" >> "${filename}"
      echo "      boundaries:" >> "${filename}"
      echo "        rot_amp: ${rot_amp_boundary}" >> "${filename}"
      echo "        con_amp: [-100.0, 100.0]" >> "${filename}"
  done
  
  # Add GP boundaries sections for indicators
  for i in "${!instruments[@]}"; do
      local instrument="${instruments[$i]}"
      for j in "${!indicators_copy[@]}"; do
          local indicator="${indicators_copy[$j]}"
          local has_rot_amp=$(get_rot_amp_setting "$j" "${#indicators_copy[@]}")
          echo "    ESSP_${indicator}_${instrument}:" >> "${filename}"
          echo "      boundaries:" >> "${filename}"
          if [ "$has_rot_amp" = "true" ]; then
              # For indicators, all rot_amp boundaries are [-10.0, 10.0]
              echo "        rot_amp: [-50.0, 50.0]" >> "${filename}"
          fi
          echo "        con_amp: [-100.0, 100.0]" >> "${filename}"
      done
  done
  
  # Add parameters section
  echo "parameters:" >> "${filename}"
  echo "  Tref: 59332.189797" >> "${filename}"
  echo "  low_ram_plot: true" >> "${filename}"
  echo "  plot_split_threshold: 1000" >> "${filename}"
  
  # Add solver section
  echo "solver:" >> "${filename}"
  echo "  pyde:" >> "${filename}"
  echo "    ngen: 50000" >> "${filename}"
  echo "    npop_mult: 12" >> "${filename}"
  echo "  emcee:" >> "${filename}"
  echo "    npop_mult: 12" >> "${filename}"
  echo "    nsteps: 25000" >> "${filename}"
  echo "    nburn: 25000" >> "${filename}"
  echo "    thin: 20" >> "${filename}"
  echo "  nested_sampling:" >> "${filename}"
  echo "    nlive: 1000" >> "${filename}"
  echo "  recenter_bounds: true" >> "${filename}"
  
  echo "✅ Generated: ${filename}"
  return 0
}

# Function to validate YAML syntax
validate_yaml() {
  local filename="$1"
  
  echo "🔍 Validating YAML syntax..."
  if command -v python3 &> /dev/null; then
      python3 -c "import yaml; yaml.safe_load(open('${filename}'))" 2>/dev/null
      if [ $? -eq 0 ]; then
          echo "✅ YAML syntax is valid"
          return 0
      else
          echo "❌ YAML syntax is invalid!"
          return 1
      fi
  elif command -v python &> /dev/null; then
      python -c "import yaml; yaml.safe_load(open('${filename}'))" 2>/dev/null
      if [ $? -eq 0 ]; then
          echo "✅ YAML syntax is valid"
          return 0
      else
          echo "❌ YAML syntax is invalid!"
          return 1
      fi
  else
      echo "⚠️  Python not found, skipping YAML validation"
      return 0
  fi
}

# Function to run PyORBIT analysis
run_pyorbit_analysis() {
  local filename="$1"
  local output_dir="$2"
  
  echo "🚀 Starting PyORBIT analysis..."
  
  # Create output directory
  mkdir -p "./${output_dir}"
  
  # Check if PyORBIT commands are available
  if ! command -v pyorbit_run &> /dev/null; then
      echo "❌ pyorbit_run command not found. Please install PyORBIT."
      return 1
  fi
  
  # Run PyORBIT
  echo "   Running emcee sampler..."
  pyorbit_run emcee "${filename}"
  
  if [ $? -eq 0 ]; then
      echo "   Generating results..."
      pyorbit_results emcee "${filename}" -all > "./${output_dir}/${output_dir}.log"
      
      # Copy config file to output directory
      cp "${filename}" "./${output_dir}/"
      
      echo "✅ Analysis completed successfully!"
      echo "   Results saved in: ./${output_dir}/"
      
      # Play completion sound (macOS)
      if command -v afplay &> /dev/null; then
          afplay /System/Library/Sounds/Glass.aiff &
      fi
      
      return 0
  else
      echo "❌ PyORBIT analysis failed!"
      return 1
  fi
}

# Main execution
main() {
  echo "🌟 PyORBIT YAML Generator and Analysis Runner"
  echo "=============================================="
  
  # Parse command line arguments
  parse_arguments "$@"
  
  # Create filename and output directory
  if [ ${#INSTRUMENTS[@]} -eq 1 ]; then
      YAML_FILE="ESSP_gp_${INSTRUMENTS[0]}.yaml"
      OUTPUT_DIR="ESSP_gp_${INSTRUMENTS[0]}"
  else
      COMBINED_INSTRUMENTS=$(IFS=_; echo "${INSTRUMENTS[*]}")
      YAML_FILE="ESSP_gp_${COMBINED_INSTRUMENTS}.yaml"
      OUTPUT_DIR="ESSP_gp_${COMBINED_INSTRUMENTS}"
  fi
  
  # Generate YAML configuration
  generate_yaml_config "${INSTRUMENTS[@]}"
  
  # Validate YAML syntax
  if ! validate_yaml "${YAML_FILE}"; then
      echo "❌ Exiting due to YAML validation error"
      exit 1
  fi
  
  # Ask user if they want to run the analysis
  echo ""
  read -p "🤔 Do you want to run the PyORBIT analysis now? (y/N): " -n 1 -r
  echo ""
  
  if [[ $REPLY =~ ^[Yy]$ ]]; then
      run_pyorbit_analysis "${YAML_FILE}" "${OUTPUT_DIR}"
  else
      echo "📋 Configuration file generated: ${YAML_FILE}"
      echo "   To run analysis later, use:"
      echo "   pyorbit_run emcee ${YAML_FILE}"
  fi
  
  echo ""
  echo "🎉 Done!"
}

# Run main function with all arguments
main "$@"
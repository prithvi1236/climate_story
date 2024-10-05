from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# Load the datasets
co2_dataset_path = 'CO2_Emissions_1960-2018.csv'
methane_dataset_path = 'methane_hist_emissions.csv'
df_co2 = pd.read_csv(co2_dataset_path)
df_methane = pd.read_csv(methane_dataset_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot_graph():
    country = request.form.get('country')

    # Check if country is available in both datasets
    co2_available = country in df_co2['Country Name'].values
    methane_available = country in df_methane['Country'].values

    if not co2_available and not methane_available:
        return jsonify({"error": "Country not found in either dataset"}), 404
    
    insights = {}
    images = []

    # Plot CO2 Emissions if available
    if co2_available:
        co2_data = df_co2[df_co2['Country Name'] == country].iloc[0, 1:]  # Exclude the country column
        img_co2 = plot_emissions(co2_data, country, "CO2 Emissions")
        images.append({'type': 'CO2', 'url': '/co2_image'})

        insights['CO2'] = {
            "Country": country,
            "Years Covered": list(co2_data.index),
            "Max Value": co2_data.max(),
            "Min Value": co2_data.min(),
            "Average Value": co2_data.mean()
        }

    # Plot Methane Emissions if available
    if methane_available:
        methane_data = df_methane[df_methane['Country'] == country].iloc[0, 1:]  # Exclude the country column
        img_methane = plot_emissions(methane_data, country, "Methane Emissions")
        images.append({'type': 'Methane', 'url': '/methane_image'})

        insights['Methane'] = {
            "Country": country,
            "Years Covered": list(methane_data.index),
            "Max Value": methane_data.max(),
            "Min Value": methane_data.min(),
            "Average Value": methane_data.mean()
        }

    # Return both images and insights as JSON
    return jsonify({
        "images": images,
        "insights": insights
    })

def plot_emissions(data, country, title):
    """ Helper function to generate and save a plot as a PNG """
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data.values, marker='o', linestyle='-', color='b')
    plt.title(f'{title} for {country}', fontsize=16)
    plt.xlabel('Year')
    plt.ylabel('Values')
    plt.grid(True)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    return img

@app.route('/co2_image')
def return_co2_image():
    country = request.args.get('country')
    if not country or country not in df_co2['Country Name'].values:
        return jsonify({"error": "Country not found in CO2 dataset"}), 404

    co2_data = df_co2[df_co2['Country Name'] == country].iloc[0, 1:]
    img = plot_emissions(co2_data, country, "CO2 Emissions")
    
    return send_file(img, mimetype='image/png')

@app.route('/methane_image')
def return_methane_image():
    country = request.args.get('country')
    if not country or country not in df_methane['Country'].values:
        return jsonify({"error": "Country not found in methane dataset"}), 404

    methane_data = df_methane[df_methane['Country'] == country].iloc[0, 1:]
    img = plot_emissions(methane_data, country, "Methane Emissions")
    
    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

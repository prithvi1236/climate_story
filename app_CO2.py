from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

app = Flask(__name__)

# Load the dataset
# Make sure the CSV file has a structure with "Country" as the first column, and the rest are years.
dataset_path = 'CO2_Emissions_1960-2018.csv'
df = pd.read_csv(dataset_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot_graph():
    country = request.form.get('country')

    if country not in df['Country Name'].values:
        return jsonify({"error": "Country not found in the dataset"}), 404
    
    # Filter the row for the inputted country
    country_data = df[df['Country Name'] == country].iloc[0, 1:]  # Exclude the country column
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(country_data.index, country_data.values, marker='o', linestyle='-', color='b')
    plt.title(f'Data for {country}', fontsize=16)
    plt.xlabel('Year')
    plt.ylabel('Values')
    plt.grid(True)
    
    # Save plot to a BytesIO object
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    
    # Insights (Example: provide some basic description of the data)
    insights = {
        "Country": country,
        "Years Covered": list(country_data.index),
        "Max Value": country_data.max(),
        "Min Value": country_data.min(),
        "Average Value": country_data.mean()
    }

    # Return both the plot image and insights as JSON
    return jsonify({
        "image": "/image",
        "insights": insights
    })

@app.route('/carbon_image')
def return_image():
    country = request.args.get('country')
    if not country or country not in df['Country Name'].values:
        return jsonify({"error": "Country not found in the dataset"}), 404
    
    country_data = df[df['Country Name'] == country].iloc[0, 1:]

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(country_data.index, country_data.values, marker='o', linestyle='-', color='b')
    plt.title(f'Data for {country}', fontsize=16)
    plt.xlabel('Year')
    plt.ylabel('Values')
    plt.grid(True)

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    return send_file(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)

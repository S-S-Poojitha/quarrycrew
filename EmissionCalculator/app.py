from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    choice = request.form.get('choice')
    output = ''

    if choice == '1':
        mineType = request.form.get('mineType1').lower()
        dieselUsage = float(request.form.get('dieselUsage'))
        electricityConsumption = float(request.form.get('electricityConsumption'))
        methaneEmissions = float(request.form.get('methaneEmissions'))
        coalProduction = float(request.form.get('coalProduction')) * 1000  # Convert to kg
        transportationDistance = float(request.form.get('transportationDistance'))
        coalTransportationWeight = float(request.form.get('coalTransportationWeight'))
        numberOfWorkers = int(request.form.get('numberOfWorkers'))
        workingHours = float(request.form.get('workingHours'))
        carbonSequestrationRate = float(request.form.get('carbonSequestrationRate'))

        factors = {
            'underground': {
                'diesel': 2.68,
                'electricity': 0.4,
                'methane': 25.0,
                'coal': 2.42,
                'transportation': 0.27
            },
            'open-cast': {
                'diesel': 2.68,
                'electricity': 0.4,
                'methane': 25.0,
                'coal': 2.42,
                'transportation': 0.27
            }
        }

        factor = factors.get(mineType, {})
        totalEmissions = (
            dieselUsage * factor['diesel'] +
            electricityConsumption * factor['electricity'] +
            methaneEmissions * factor['methane'] +
            coalProduction * factor['coal'] +
            transportationDistance * coalTransportationWeight * factor['transportation']
        )

        perCapitaEmissions = totalEmissions / (numberOfWorkers * workingHours)
        requiredLand = totalEmissions / carbonSequestrationRate

        output = f"Total emissions for {mineType} mine: {totalEmissions:.2f} kg CO2<br>"
        output += f"Per capita emissions: {perCapitaEmissions:.6f} kg CO2<br>"
        output += f"Land required for afforestation: {requiredLand:.2f} hectares"

    elif choice == '2':
        mineType = request.form.get('mineType2').lower()
        activity = request.form.get('activity').lower()
        amount = float(request.form.get('amount'))
        numberOfWorkers = int(request.form.get('numberOfWorkers2'))
        workingHours = float(request.form.get('workingHours2'))

        factors = {
            'diesel': 2.68,
            'electricity': 0.4,
            'methane': 25.0,
            'coal': 2.42,
            'transportation': 0.27
        }

        emission = amount * factors.get(activity, 0)
        perCapitaEmissions = emission / (numberOfWorkers * workingHours)

        output = f"Emissions for {activity}: {emission:.2f} kg CO2<br>"
        output += f"Per capita emissions for {activity}: {perCapitaEmissions:.6f} kg CO2"

    return output

if __name__ == '__main__':
    app.run(debug=True)

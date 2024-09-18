from flask import Flask, render_template, request

app = Flask(__name__)

# Mock AI suggestion function
def generate_ai_suggestions(mine_type, emission_gap):
    suggestions = []

    if mine_type == "underground":
        suggestions.append("Adopt electric-powered machinery to reduce diesel emissions.")
        suggestions.append("Implement methane capture systems to prevent greenhouse gas release.")
    elif mine_type == "open_cast":
        suggestions.append("Increase vegetation around the mine to improve carbon absorption.")
        suggestions.append("Switch to solar-powered conveyor belts to reduce electricity use.")

    # Common suggestions
    if emission_gap > 0:
        suggestions.append("Consider purchasing carbon credits to offset the remaining emissions.")
        suggestions.append("Explore renewable energy sources like solar or wind to reduce fossil fuel dependency.")

    return suggestions

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        land_area = float(request.form['land_area'])
        mine_type = request.form['mine_type']
        emissions = float(request.form['emissions'])

        # Example: Simple absorption estimation (these numbers would be based on real data)
        if mine_type == "underground":
            absorption = land_area * 10  # Placeholder calculation
        else:
            absorption = land_area * 15  # Placeholder calculation

        emission_gap = emissions - absorption
        suggestions = generate_ai_suggestions(mine_type, emission_gap)

        return render_template('index.html', land_area=land_area, mine_type=mine_type,
                               emissions=emissions, absorption=absorption, 
                               emission_gap=emission_gap, suggestions=suggestions)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

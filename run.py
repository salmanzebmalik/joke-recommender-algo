from app import create_app
import os
# Create the Flask app instance
app = create_app()

# Run the Flask development server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)

from flask import Flask, jsonify
from flask_cors import CORS
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import API_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """
    Application factory pattern untuk Flask app
    """
    app = Flask(__name__)
    
    # Enable CORS untuk semua routes
    CORS(app)
    
    # Configuration
    app.config.update(API_CONFIG)
    
    # ==================== MANUAL BLUEPRINT REGISTRATION ====================
    print("🔧 Registering blueprints...")
    
    try:
        # Register transactions blueprint
        from routes.transactions import transactions_bp
        app.register_blueprint(transactions_bp, url_prefix='/api/v1/transactions')
        print("✅ Transactions blueprint registered")
    except Exception as e:
        print(f"❌ Transactions blueprint failed: {e}")
    
    try:
        # Register analytics blueprint
        from routes.analytics import analytics_bp
        app.register_blueprint(analytics_bp, url_prefix='/api/v1/analytics')
        print("✅ Analytics blueprint registered")
    except Exception as e:
        print(f"❌ Analytics blueprint failed: {e}")
    
    try:
        # Register AI blueprint - FORCE IMPORT
        print("🔄 Attempting to import AI blueprint...")
        from routes.ai_routes import ai_bp
        print("✅ AI blueprint imported successfully")
        
        app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')
        print("✅ AI blueprint registered")
        
        # Test if AI routes are accessible
        print("🎯 AI endpoints registered:")
        for rule in app.url_map.iter_rules():
            if 'ai' in rule.rule:
                print(f"   - {rule.rule}")
                
    except Exception as e:
        print(f"❌ AI blueprint failed: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")
    
    # ==================== DEBUG ROUTES ====================
    @app.route('/debug/routes')
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            if not rule.rule.startswith('/static'):
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': list(rule.methods),
                    'path': str(rule)
                })
        return jsonify({"routes": routes, "count": len(routes)})
    
    # Health check endpoint
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "service": "Smart Finance API"
        })
    
    # Test AI endpoint
    @app.route('/api/v1/ai/test', methods=['GET'])
    def test_ai():
        return jsonify({
            "status": "success", 
            "message": "AI test endpoint is working!",
            "endpoints_available": True
        })
    
    print("🎉 Flask app initialization completed")
    return app

if __name__ == '__main__':
    app = create_app()
    print("\n🚀 Starting Flask API Server...")
    print("📍 Available endpoints:")
    print("   http://127.0.0.1:5000/api/v1/health")
    print("   http://127.0.0.1:5000/api/v1/ai/test")
    print("   http://127.0.0.1:5000/debug/routes")
    print("\n")
    
    app.run(
        host=API_CONFIG['HOST'],
        port=API_CONFIG['PORT'], 
        debug=API_CONFIG['DEBUG']
    )
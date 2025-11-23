from flask import jsonify

def register_error_handlers(app):
    """
    Register global error handlers
    """
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "status": "error",
            "message": "Resource not found",
            "error": str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "status": "error", 
            "message": "Internal server error",
            "error": str(error)
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "status": "error",
            "message": "Bad request",
            "error": str(error)
        }), 400
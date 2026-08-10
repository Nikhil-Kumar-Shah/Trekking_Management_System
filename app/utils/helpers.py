import random
import string

def generate_certificate_code(booking_id):
    """
    Generate a unique certificate number using booking identifier and randomized tokens.
    Format: TRK-<booking_id>-<random_chars>
    """
    character_pool = string.ascii_uppercase + string.digits
    random_token = ''.join(random.choices(character_pool, k=6))
    
    # Format code with zero-padded booking ID
    certificate_code = f"TRK-{booking_id:04d}-{random_token}"
    return certificate_code

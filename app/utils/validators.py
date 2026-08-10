from wtforms import ValidationError

def validate_trek_dates(form, field):
    """
    Ensure the trek ending date is not scheduled before the starting date.
    """
    start_date = form.start_date.data
    end_date = form.end_date.data
    
    if start_date:
        if end_date:
            if end_date < start_date:
                raise ValidationError("The end date cannot be scheduled before the start date.")

import jaconv
from django.db import models

class TextNormalizationMixin:
    """
    Mixin to automatically normalize text fields:
    1. Convert half-width katakana to full-width katakana
    2. Convert full-width numbers to half-width numbers
    3. Convert full-width alphabets to half-width alphabets
    """

    def save(self, *args, **kwargs):
        # Get all text-based fields from the model
        for field in self._meta.fields:
            if isinstance(field, (models.CharField, models.TextField)):
                field_name = field.name
                current_value = getattr(self, field_name)

                # Apply conversions only if the field has a value
                if current_value and isinstance(current_value, str):
                    # Step 1: Convert half-width kana to full-width kana
                    converted_value = jaconv.h2z(current_value, kana=True, ascii=False, digit=False)

                    # Step 2: Convert full-width numbers to half-width numbers
                    converted_value = jaconv.z2h(converted_value, kana=False, ascii=False, digit=True)

                    # Step 3: Convert full-width alphabets to half-width alphabets
                    converted_value = jaconv.z2h(converted_value, kana=False, ascii=True, digit=False)

                    setattr(self, field_name, converted_value)

        # Call the original save method
        super().save(*args, **kwargs)

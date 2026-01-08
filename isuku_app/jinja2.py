"""
Jinja2 environment configuration for Django
"""
from jinja2 import Environment
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.translation import gettext, gettext_lazy, pgettext
from django.utils import translation
from django.template.defaultfilters import date as django_date
import os
from urllib.parse import quote, urlparse, urlunparse


def environment(**options):
    env = Environment(**options)
    
    def url(name, *args, **kwargs):
        return reverse(name, args=args, kwargs=kwargs)
    
    def static_file(path):
        """Get static file URL, handling spaces in filenames"""
        from django.conf import settings
        try:
            # Try to get the URL directly
            url_path = staticfiles_storage.url(path)
            # URL encode spaces in the final URL if needed
            if ' ' in url_path:
                # Encode spaces and other special characters in the URL
                parsed = urlparse(url_path)
                # Encode the path part
                encoded_path = quote(parsed.path, safe='/')
                # Reconstruct the URL
                url_path = urlunparse((parsed.scheme, parsed.netloc, encoded_path, 
                                      parsed.params, parsed.query, parsed.fragment))
            return url_path
        except Exception as e:
            # Fallback: manually construct URL with proper encoding
            # Split the path and encode each part (but keep slashes)
            path_parts = path.split('/')
            encoded_parts = [quote(part, safe='') for part in path_parts]
            encoded_path = '/'.join(encoded_parts)
            # Return with STATIC_URL
            return f"{settings.STATIC_URL}{encoded_path}"
    
    def gettext_func(message):
        """Translation function for Jinja2 - uses current language from thread"""
        # This will use the language set by LocaleMiddleware
        return gettext(message)
    
    def ngettext_func(singular, plural, n):
        """Plural translation function for Jinja2"""
        from django.utils.translation import ngettext
        return ngettext(singular, plural, n)
    
    def get_current_language():
        """Get current language code"""
        return translation.get_language()
    
    def get_available_languages():
        """Get available languages"""
        from django.conf import settings
        return settings.LANGUAGES
    
    def date_filter(value, arg=None):
        """Date filter for Jinja2 templates"""
        if value is None:
            return ''
        try:
            return django_date(value, arg)
        except:
            # Fallback to strftime if Django date filter fails
            if hasattr(value, 'strftime'):
                if arg:
                    # Convert Django date format to strftime format
                    format_map = {
                        'M': '%b',  # Short month name
                        'd': '%d',  # Day of month
                        'Y': '%Y',  # 4-digit year
                        'm': '%m',  # Month as number
                        'y': '%y',  # 2-digit year
                    }
                    strftime_format = arg
                    for django_fmt, strftime_fmt in format_map.items():
                        strftime_format = strftime_format.replace(django_fmt, strftime_fmt)
                    return value.strftime(strftime_format)
                return value.strftime('%b %d, %Y')
            return str(value)
    
    def format_filter(value, format_str):
        """Format filter for Jinja2 templates"""
        try:
            if isinstance(value, (int, float)):
                return format_str % value
            return str(value)
        except:
            return str(value)
    
    def waste_category_badge(category):
        """Generate HTML badge for waste category with color and icon"""
        if not category:
            return ''
        color = category.color_code if hasattr(category, 'color_code') else '#059669'
        icon = category.icon if hasattr(category, 'icon') and category.icon else 'fa-trash-alt'
        name = category.name if hasattr(category, 'name') else str(category)
        
        # Map common waste types to icons if not set
        icon_map = {
            'Organic Waste': 'fa-leaf',
            'Plastic Waste': 'fa-wine-bottle',
            'Paper Waste': 'fa-file-alt',
            'Glass Waste': 'fa-wine-glass',
            'Metal Waste': 'fa-cog',
            'General Waste': 'fa-trash-alt',
        }
        
        if not icon or icon == '':
            icon = icon_map.get(name, 'fa-trash-alt')
        
        return f'<span class="waste-category-badge" style="background-color: {color}20; color: {color}; border: 1px solid {color}40; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;"><i class="fas {icon}"></i> {name}</span>'
    
    env.filters['date'] = date_filter
    env.filters['format'] = format_filter
    env.filters['waste_category_badge'] = waste_category_badge
    
    env.globals.update({
        'static': static_file,
        'url': url,
        'get_messages': get_messages,
        '_': gettext_func,
        'gettext': gettext_func,
        'ngettext': ngettext_func,
        'get_language': get_current_language,
        'get_available_languages': get_available_languages,
    })
    
    return env


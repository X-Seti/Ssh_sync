#!/usr/bin/env python3

"""
X-Seti - July03 2023 - SSH File Sync - Icon Methods Module - version 3
this belongs in apps/methods/sshsync_svgicons.py

Shared SVG icon creation methods
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray


def svg_to_icon(svg_data, size=24):
    """Convert SVG data to QIcon with theme color support"""
    try:
        # Create SVG renderer
        renderer = QSvgRenderer(QByteArray(svg_data))
        
        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        # Render SVG
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
        
    except Exception as e:
        print(f"Error creating icon: {e}")
        return QIcon()


def create_info_icon(size=20):
    """Info - circle with 'i'"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none"/>
        <line x1="12" y1="16" x2="12" y2="12" stroke="currentColor" stroke-width="2"/>
        <circle cx="12" cy="8" r="0.5" fill="currentColor"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_settings_icon(size=20):
    """Settings/gear icon"""
    svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
        <path d="M10 2v2M10 16v2M2 10h2M16 10h2M4.93 4.93l1.41 1.41M13.66 13.66l1.41 1.41M4.93 15.07l1.41-1.41M13.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_theme_icon(size=20):
    """Theme/palette icon"""
    svg_data = b'''<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M10 2C5.58 2 2 5.58 2 10c0 4.42 3.58 8 8 8 .5 0 1-.4 1-1 0-.25-.1-.48-.24-.65-.14-.17-.24-.42-.24-.65 0-.55.45-1 1-1h1.5c2.48 0 4.5-2.02 4.5-4.5C17.52 5.58 14.42 2 10 2z" stroke="currentColor" stroke-width="1.5" fill="none"/>
        <circle cx="5.5" cy="10" r="1" fill="currentColor"/>
        <circle cx="8" cy="7" r="1" fill="currentColor"/>
        <circle cx="12" cy="7" r="1" fill="currentColor"/>
        <circle cx="14.5" cy="10" r="1" fill="currentColor"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_minimize_icon(size=20):
    """Minimize window icon"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_maximize_icon(size=20):
    """Maximize window icon"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <rect x="6" y="6" width="12" height="12" stroke="currentColor" stroke-width="2" fill="none"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_close_icon(size=20):
    """Close window icon"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
        <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_import_icon(size=20):
    """Import - Download arrow icon"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
            stroke="currentColor" stroke-width="2"
            fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="7 10 12 15 17 10"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="12" y1="15" x2="12" y2="3"
            stroke="currentColor" stroke-width="2"
            stroke-linecap="round"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_export_icon(size=20):
    """Export - Upload arrow icon"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"
            stroke="currentColor" stroke-width="2"
            fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline points="17 8 12 3 7 8"
                stroke="currentColor" stroke-width="2"
                fill="none" stroke-linecap="round" stroke-linejoin="round"/>
        <line x1="12" y1="3" x2="12" y2="15"
            stroke="currentColor" stroke-width="2"
            stroke-linecap="round"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_rename_icon(size=20):
    """Rename icon - pencil/edit"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"
            stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"
            stroke="currentColor" stroke-width="2" fill="none"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_ignore_icon(size=20):
    """Ignore icon - eye with slash"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"
            stroke="currentColor" stroke-width="2" fill="none"/>
        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2" fill="none"/>
        <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_find_icon(size=20):
    """Find icon - magnifying glass"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2" fill="none"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65" stroke="currentColor" stroke-width="2"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_replace_icon(size=20):
    """Replace icon - swap arrows"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <polyline points="17 1 21 5 17 9" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M3 11V9a4 4 0 014-4h14" stroke="currentColor" stroke-width="2" fill="none"/>
        <polyline points="7 23 3 19 7 15" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M21 13v2a4 4 0 01-4 4H3" stroke="currentColor" stroke-width="2" fill="none"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_adddir_icon(size=20):
    """Add Directory icon - folder with plus"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"
            stroke="currentColor" stroke-width="2" fill="none"/>
        <line x1="12" y1="11" x2="12" y2="17" stroke="currentColor" stroke-width="2"/>
        <line x1="9" y1="14" x2="15" y2="14" stroke="currentColor" stroke-width="2"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_delete_icon(size=20):
    """Delete icon - trash can"""
    svg_data = b'''<svg viewBox="0 0 24 24">
        <polyline points="3 6 5 6 21 6" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
            stroke="currentColor" stroke-width="2" fill="none"/>
        <line x1="10" y1="11" x2="10" y2="17" stroke="currentColor" stroke-width="2"/>
        <line x1="14" y1="11" x2="14" y2="17" stroke="currentColor" stroke-width="2"/>
    </svg>'''
    return svg_to_icon(svg_data, size)


def create_app_icon_pixmap(size=32):
    """Create application icon - two computers with sync arrows and lock"""
    svg_data = f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64">
        <!-- Left computer -->
        <rect x="4" y="12" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
        <rect x="8" y="28" width="14" height="2" fill="currentColor"/>
        <line x1="15" y1="30" x2="15" y2="34" stroke="currentColor" stroke-width="2"/>
        <line x1="10" y1="34" x2="20" y2="34" stroke="currentColor" stroke-width="2"/>
        
        <!-- Right computer -->
        <rect x="38" y="12" width="22" height="16" rx="2" stroke="currentColor" stroke-width="2" fill="none"/>
        <rect x="42" y="28" width="14" height="2" fill="currentColor"/>
        <line x1="49" y1="30" x2="49" y2="34" stroke="currentColor" stroke-width="2"/>
        <line x1="44" y1="34" x2="54" y2="34" stroke="currentColor" stroke-width="2"/>
        
        <!-- Sync arrows -->
        <path d="M26 16 L34 16" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M30 13 L34 16 L30 19" stroke="currentColor" stroke-width="2" fill="none"/>
        
        <path d="M38 24 L30 24" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M34 21 L30 24 L34 27" stroke="currentColor" stroke-width="2" fill="none"/>
        
        <!-- Lock symbol (security) -->
        <rect x="26" y="42" width="12" height="10" rx="1" stroke="currentColor" stroke-width="2" fill="none"/>
        <path d="M28 42 v-3 a4 4 0 0 1 8 0 v3" stroke="currentColor" stroke-width="2" fill="none"/>
        <circle cx="32" cy="47" r="1.5" fill="currentColor"/>
    </svg>'''
    
    from PyQt6.QtGui import QPixmap, QPainter
    from PyQt6.QtSvg import QSvgRenderer
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtGui import QColor
    
    renderer = QSvgRenderer(QByteArray(svg_data.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return pixmap

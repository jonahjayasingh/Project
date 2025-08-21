import React, { useState, useEffect } from 'react';
import { View, Text, Pressable, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function Navbar({ title = 'MyApp', links = [], onBack, rightIcon, onRightPress }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detect screen width on web
  useEffect(() => {
    if (Platform.OS === 'web') {
      const handleResize = () => setIsMobile(window.innerWidth < 768);
      handleResize();
      window.addEventListener('resize', handleResize);
      return () => window.removeEventListener('resize', handleResize);
    }
  }, []);

  const handleLink = (href) => {
    if (Platform.OS === 'web') {
      window.location.href = href;
    } else {
      console.log('Navigate to', href);
    }
  };

  if (Platform.OS === 'web') {
    // Web version with Bootstrap
    return (
      <nav className="navbar navbar-expand-md navbar-light bg-light">
        <div className="container-fluid">
          <a className="navbar-brand" href="/">{title}</a>

          {/* Hamburger button for mobile */}
          {isMobile && (
            <button
              className="navbar-toggler"
              type="button"
              onClick={() => setMenuOpen(!menuOpen)}
            >
              <span className="navbar-toggler-icon"></span>
            </button>
          )}

          <div className={`collapse navbar-collapse ${menuOpen ? 'show' : ''}`}>
            <ul className="navbar-nav ms-auto mb-2 mb-md-0">
              {links.map((link, idx) => (
                <li className="nav-item" key={idx}>
                  <a className="nav-link" href={link.href}>{link.label}</a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </nav>
    );
  }

  // Android/React Native version
  return (
    <SafeAreaView edges={['top']} style={{ backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#ddd' }}>
      <View style={{ flexDirection: 'row', height: 56, alignItems: 'center', paddingHorizontal: 12, justifyContent: 'space-between' }}>
        <View>
          {onBack ? (
            <Pressable onPress={onBack}>
              <Ionicons name="chevron-back" size={26} color="#111" />
            </Pressable>
          ) : (
            <Text style={{ fontSize: 18, fontWeight: '700' }}>{title}</Text>
          )}
        </View>
        {rightIcon && (
          <Pressable onPress={onRightPress}>
            <Ionicons name={rightIcon} size={24} color="#111" />
          </Pressable>
        )}
      </View>
    </SafeAreaView>
  );
}

import React from 'react';
import { View, Text } from 'react-native';
import Navbar from './components/Navbar';

export default function index() {
  return (
    <View style={{ flex: 1 }}>
      <Navbar
        title="MyApp"
        links={[
          { label: 'Home', href: '/' },
          { label: 'Features', href: '/features' },
          { label: 'Pricing', href: '/pricing' },
          { label: 'About', href: '/about' },
        ]}
        rightIcon="save-outline"
        onRightPress={() => console.log('Save pressed')}
      />
      <View style={{ flex: 1, padding: 16 }}>
        <Text>Universal content for both Android and Web!</Text>
      </View>
    </View>
  );
}

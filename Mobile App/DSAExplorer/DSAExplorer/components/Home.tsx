import { Animated, View, Text, TouchableOpacity, SafeAreaView, Platform } from 'react-native';
import { useEffect, useRef, useState } from 'react';
import { useNavigation } from '@react-navigation/native';
import type { NativeStackNavigationProp } from '@react-navigation/native-stack';

// Define navigation types (inline for single file)
type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  Register: undefined;
  Main: undefined;
  // Add other screens as needed
};

type HomeScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Home'>;

export const Home = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const fadeAnim = useRef(new Animated.Value(0)).current;
  const [pressAnim] = useState(new Animated.Value(1));

  useEffect(() => {
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 1000,
      useNativeDriver: true,
    }).start();
  }, []);

  const onPressIn = () => {
    Animated.spring(pressAnim, {
      toValue: 0.96,
      useNativeDriver: true,
      speed: 12,
    }).start();
  };

  const onPressOut = () => {
    Animated.spring(pressAnim, {
      toValue: 1,
      friction: 5,
      tension: 40,
      useNativeDriver: true,
    }).start();
  };

  return (
    <SafeAreaView className={`flex-1 bg-white px-6 ${Platform.OS === 'ios' ? 'pt-0' : 'pt-6'} justify-between`}>
      {/* Animated Header Section */}
      <Animated.View style={{ opacity: fadeAnim, alignItems: 'center', marginTop: 80 }}>
        <Text className="text-4xl font-extrabold text-indigo-700 text-center tracking-tight">
          DSAExplorer
        </Text>
        <Text className="mt-3 text-gray-600 text-center text-lg leading-6 px-4">
          Master Data Structures & Algorithms with interactive visualizations.
        </Text>
      </Animated.View>

      {/* Action Button */}
      <View className="items-center mb-12">
        <TouchableOpacity
          onPress={() => navigation.navigate('Login')}
          onPressIn={onPressIn}
          onPressOut={onPressOut}
          className="bg-indigo-600 py-4 px-8 rounded-2xl shadow-md active:bg-indigo-700 web:hover:bg-indigo-700 web:cursor-pointer"
          accessibilityRole="button"
          accessibilityLabel="Start exploring algorithms"
        >
          <Animated.Text
            style={{
              color: 'white',
              fontSize: 18,
              fontWeight: '600',
              textAlign: 'center',
              transform: [{ scale: pressAnim }],
            }}
          >
            Get Started
          </Animated.Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};
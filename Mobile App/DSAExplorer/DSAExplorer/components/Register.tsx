import React, { useState,useEffect } from 'react';
import { Text, View, TextInput, TouchableOpacity, Alert, ActivityIndicator,Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';

type RootStackParamList = {
  Home: undefined;
  Login: undefined;
  Register: undefined;
  Main: undefined;
};

type RegisterScreenNavigationProp = NativeStackNavigationProp<RootStackParamList, 'Register'>;

// API base URL - adjust to your actual backend URL
// Common local IP patterns: 192.168.1.X, 192.168.0.X, 10.0.2.2 (for Android emulator)
const API_BASE_URL = Platform.OS === 'web' ? 'http://127.0.0.1:8000' : 'http://10.0.2.2:8000'; // Fixed IP address



export const Register = () => {
  const navigation = useNavigation<RegisterScreenNavigationProp>();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async () => {
    console.log("Registration started");
    
const showError = (message: string) => {
  if (Platform.OS === 'web') {
    window.alert(message);
  } else {
    Alert.alert('Error', message);
  }
};

if (!username || !password || !confirmPassword) {
  showError('Please fill all fields');
  return;
}

if (password !== confirmPassword) {
  showError('Passwords do not match');
  return;
}

if (password.length < 6) {
  showError('Password should be at least 6 characters long');
  return;
}


    setIsLoading(true);
    console.log("Making API call to:", `${API_BASE_URL}/register`);
    
    try {
      // Make API call to your FastAPI register endpoint
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username,
          password: password
        }),
      });

      console.log("Response status:", response.status);
      
      let data;
      try {
        data = await response.json();
        console.log("Response data:", data);
      } catch (jsonError) {
        console.log("JSON parse error:", jsonError);
        throw new Error('Invalid response from server');
      }

      if (response.ok) {
        Alert.alert('Success', 'Account created successfully');
        navigation.replace('Login');
      } else {
        Alert.alert('Registration Failed', data.detail || 'An error occurred during registration');
      }
    } catch (error) {
      console.error('Registration error:', error);
      Alert.alert('Error', 'Network error. Please try again. Check if server is running and IP is correct.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white px-6 justify-center">
      <View className='w-80 mx-auto'>
        <Text className="text-3xl font-bold text-indigo-700 text-center mb-10">
          Create your account
        </Text>

        <TextInput
          className="border border-gray-300 rounded-xl px-4 py-3 mb-6 text-base text-gray-900"
          placeholder="Username"
          autoCapitalize="none"
          value={username}
          onChangeText={setUsername}
          placeholderTextColor="#9CA3AF"
        />

        <TextInput
          className="border border-gray-300 rounded-xl px-4 py-3 mb-6 text-base text-gray-900"
          placeholder="Password"
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          placeholderTextColor="#9CA3AF"
        />

        <TextInput
          className="border border-gray-300 rounded-xl px-4 py-3 mb-8 text-base text-gray-900"
          placeholder="Confirm Password"
          secureTextEntry
          value={confirmPassword}
          onChangeText={setConfirmPassword}
          placeholderTextColor="#9CA3AF"
        />

        <TouchableOpacity
          className="bg-indigo-600 rounded-xl py-4 mb-4"
          onPress={handleRegister}
          activeOpacity={0.8}
          accessibilityRole="button"
          accessibilityLabel="Register"
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text className="text-white text-center text-lg font-semibold">Register</Text>
          )}
        </TouchableOpacity>

        <View className="flex-row justify-center">
          <Text className="text-gray-600 mr-2">Already have an account?</Text>
          <TouchableOpacity onPress={() => navigation.navigate('Login')}>
            <Text className="text-indigo-600 font-semibold">Login</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
};  
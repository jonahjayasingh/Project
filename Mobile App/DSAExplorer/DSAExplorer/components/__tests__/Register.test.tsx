import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Register } from '../Register';
import { useNavigation } from '@react-navigation/native';

// Mock useNavigation
const mockedNavigate = jest.fn();
const mockedReplace = jest.fn();
jest.mock('@react-navigation/native', () => ({
  useNavigation: () => ({
    navigate: mockedNavigate,
    replace: mockedReplace,
  }),
}));

// Mock fetch
global.fetch = jest.fn();

describe('Register Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    const { getByPlaceholderText, getByText } = render(<Register />);
    
    expect(getByText('Create your account')).toBeTruthy();
    expect(getByPlaceholderText('Username')).toBeTruthy();
    expect(getByPlaceholderText('Password')).toBeTruthy();
    expect(getByPlaceholderText('Confirm Password')).toBeTruthy();
  });

  it('calls handleRegister on successful input', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'User created' }),
    });

    const { getByPlaceholderText, getByText } = render(<Register />);
    
    fireEvent.changeText(getByPlaceholderText('Username'), 'testuser');
    fireEvent.changeText(getByPlaceholderText('Password'), 'password123');
    fireEvent.changeText(getByPlaceholderText('Confirm Password'), 'password123');
    fireEvent.press(getByText('Register'));

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/register'),
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(mockedReplace).toHaveBeenCalledWith('Login');
    });
  });
});

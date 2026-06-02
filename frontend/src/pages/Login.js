import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Tab,
  Tabs,
  Alert,
} from '@mui/material';
import { useMutation } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

function Login() {
  const navigate = useNavigate();
  const [tab, setTab] = useState(0);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');

  const adminLoginMutation = useMutation(
    async (data) => {
      const response = await axios.post('http://13.205.70.46:8000/api/auth/admin/login', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userType', data.user_type);
        localStorage.setItem('userId', data.user_id);
        toast.success('Login successful!');
        navigate('/admin/dashboard');
      },
      onError: (error) => {
        setError(error.response?.data?.detail || 'Login failed');
        toast.error('Login failed');
      },
    }
  );

  const tenantLoginMutation = useMutation(
    async (data) => {
      const response = await axios.post('http://13.205.70.46:8000/api/auth/tenant/login', data);
      return response.data;
    },
    {
      onSuccess: (data) => {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userType', data.user_type);
        localStorage.setItem('userId', data.user_id);
        toast.success('Login successful!');
        navigate('/tenant/dashboard');
      },
      onError: (error) => {
        setError(error.response?.data?.detail || 'Login failed');
        toast.error('Login failed');
      },
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    if (tab === 0) {
      adminLoginMutation.mutate({ email, password });
    } else {
      tenantLoginMutation.mutate({ username, password });
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center" gutterBottom>
            Shop Rent Management System
          </Typography>

          <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 3 }}>
            <Tab label="Admin Login" />
            <Tab label="Tenant Login" />
          </Tabs>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <form onSubmit={handleSubmit}>
            {tab === 0 ? (
              <>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  autoFocus
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                />
              </>
            ) : (
              <>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  autoFocus
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </>
            )}

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={adminLoginMutation.isLoading || tenantLoginMutation.isLoading}
            >
              Sign In
            </Button>
          </form>

          <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 2 }}>
            Default Admin: admin@shoprent.com / Admin@123
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}

export default Login;
import React from 'react';
import { Box, Grid, Stat, StatLabel, StatNumber, Card, SimpleGrid, Heading, Text } from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const Dashboard = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const stats = [
    { label: 'Total Orders', value: '0' },
    { label: 'Active Conversations', value: '0' },
    { label: 'Products', value: '0' },
  ];

  const menuItems = [
    { title: 'Products', description: 'Manage your product catalog', path: '/products' },
    { title: 'Orders', description: 'View and manage orders', path: '/orders' },
    { title: 'Chat History', description: 'View conversation history', path: '/conversations' },
    { title: 'Settings', description: 'Configure your shop settings', path: '/settings' },
  ];

  return (
    <Box p={8}>
      <Heading mb={6}>Welcome, {user?.instagram_handle}</Heading>
      
      {/* Stats Overview */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} mb={8}>
        {stats.map((stat) => (
          <Stat key={stat.label} p={4} bg="white" borderRadius="lg" boxShadow="sm">
            <StatLabel fontSize="lg">{stat.label}</StatLabel>
            <StatNumber fontSize="3xl">{stat.value}</StatNumber>
          </Stat>
        ))}
      </SimpleGrid>

      {/* Navigation Cards */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
        {menuItems.map((item) => (
          <Card 
            key={item.title}
            p={6}
            cursor="pointer"
            onClick={() => navigate(item.path)}
            _hover={{ transform: 'translateY(-2px)', transition: 'all 0.2s' }}
          >
            <Heading size="md" mb={2}>{item.title}</Heading>
            <Text color="gray.600">{item.description}</Text>
          </Card>
        ))}
      </Grid>
    </Box>
  );
};

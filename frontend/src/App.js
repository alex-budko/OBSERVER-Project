import React, { useState } from "react";
import {
  Box,
  VStack,
  Input,
  Button,
  Textarea,
  Heading,
  Center,
} from "@chakra-ui/react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");

  const handleInputChange = (event) => {
    setMessage(event.target.value);
  };

  const handleResponseGeneration = async () => {
    try {
      const result = await axios.post(
        "http://localhost:5000/api/generate-response",
        { message, category: 'Risk factors for disease' },
        { headers: { 'Content-Type': 'application/json' } }
      );
      console.log(result)
      setResponse(result.data.response);
    } catch (error) {
      console.error("Error generating response:", error);
      setResponse("Error generating response");
    }
  };

  return (
    <Box
      className="app"
      minH="100vh"
      bgGradient="linear(to-r, blue.200, purple.500)"
    >
      <Center>
        <VStack
          mt="5"
          padding={10}
          spacing={5}
          alignItems="stretch"
          maxW="md"
          borderRadius="md"
          bg="white"
          boxShadow="dark-lg"
          rounded='3xl'
          p={6}
        >
          <Heading size="xl" textAlign="center">
            Patient-Doctor Message Simulator
          </Heading>
          <Input
            placeholder="Type your message as a patient here..."
            value={message}
            onChange={handleInputChange}
            bg="gray.50"
            borderColor="gray.300"
            _hover={{ borderColor: "gray.500" }}
            _focus={{
              borderColor: "blue.500",
              boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)",
            }}
          />
          <Button colorScheme="blue" onClick={handleResponseGeneration}>
            Generate Response
          </Button>
          <Textarea
            isReadOnly
            value={response}
            placeholder="Generated response will appear here..."
            bg="gray.50"
            borderColor="gray.300"
            _hover={{ borderColor: "gray.500" }}
            _focus={{
              borderColor: "blue.500",
              boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.6)",
            }}
          />
        </VStack>
      </Center>
    </Box>
  );
}

export default App;

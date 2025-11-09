# Implementation Plan - Nino Educational Agent

- [x] 1. Set up project structure and configuration



  - Create main project directory structure (src/, config/, etc.)
  - Create .env.example file with all required environment variables
  - Create requirements.txt with FastAPI, LangChain, OpenAI, httpx, python-dotenv, uvicorn
  - Create config.py to load and validate environment variables
  - Create README.md with setup instructions for virtual environment




  - _Requirements: 5.1, 5.2, 5.3, 6.1, 6.2, 6.3_

- [ ] 2. Implement Evolution API client
  - [ ] 2.1 Create EvolutionAPIClient class with async send_message method
    - Implement async HTTP POST using httpx




    - Add proper headers (apikey, Content-Type)
    - Format request body with number and text fields
    - Add error logging for failed requests
    - Return boolean success status
    - _Requirements: 2.1, 2.2, 2.3, 2.4_


- [ ] 3. Implement LangChain agent with dual-mode prompts
  - [ ] 3.1 Create NinoAgent class with LangChain integration
    - Initialize ChatOpenAI with model and temperature from config
    - Create system prompt with dual-mode instructions (empathetic + academic)
    - Set up ChatPromptTemplate with system message and MessagesPlaceholder
    - Implement memory dictionary indexed by phone number




    - Create get_or_create_memory method for ConversationBufferWindowMemory
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [ ] 3.2 Implement async generate_response method
    - Retrieve or create memory for phone number




    - Create LangChain chain with prompt, LLM, and memory
    - Invoke chain with user message
    - Return generated response text
    - Handle LLM errors with fallback message
    - _Requirements: 4.1, 4.2_

- [ ] 4. Implement message processor
  - [x] 4.1 Create MessageProcessor class

    - Initialize with NinoAgent and EvolutionAPIClient instances
    - Implement async process_message method
    - Call NinoAgent to generate response
    - Call EvolutionAPIClient to send response
    - Add error handling and logging
    - _Requirements: 1.2, 2.1, 3.3, 4.1_



- [ ] 5. Implement FastAPI webhook handler
  - [ ] 5.1 Create FastAPI application and webhook endpoint
    - Initialize FastAPI app
    - Create POST /webhook endpoint
    - Define request model for Evolution API payload structure

    - Implement payload validation
    - Extract phone number from remoteJid field
    - Extract message text from message.conversation field
    - Return 200 OK response
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [ ] 5.2 Integrate webhook with message processor
    - Instantiate MessageProcessor in app startup
    - Call process_message from webhook endpoint
    - Handle async processing
    - Add error handling for invalid payloads (return 400)
    - Add error handling for processing failures (return 500)
    - _Requirements: 1.2, 1.3, 1.4_

- [ ] 6. Create main application entry point
  - Create main.py that initializes FastAPI app
  - Add startup event to validate environment variables
  - Add health check endpoint GET /health
  - Configure uvicorn settings (host, port from env)
  - Add logging configuration
  - _Requirements: 5.1, 5.2, 5.4_

- [x] 7. Create documentation and setup files

  - Write README.md with virtual environment setup instructions
  - Document Evolution API webhook configuration steps
  - Add .env.example with all required variables
  - Add .gitignore for venv/, .env, __pycache__
  - Document how to run the application with uvicorn
  - _Requirements: 6.3, 6.4_

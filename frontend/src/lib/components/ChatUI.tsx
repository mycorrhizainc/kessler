"use client";
import {
  Center,
  Button,
  IconButton,
  VStack,
  StackDivider,
  Box,
  Grid,
  GridItem,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalCloseButton,
  Text,
  Select,
  SkeletonText,
} from "@chakra-ui/react";
import {
  Form,
  FormLayout,
  Field,
} from "@saas-ui/react";
import { FiArrowUpCircle } from "react-icons/fi";
import { useState, useEffect } from "react";
import { useColorMode } from "@chakra-ui/react";

import MarkdownRenderer from "./MarkdownRenderer";

function SourceModal() {
  // full screen modal for a given source
  // TODO: cache the sourceModal text in the zustand state manager
  return (
    <Box>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur
      ultricies vehicula velit, at condimentum diam tristique a. Sed commodo,
      metus quis scelerisque porta, turpis libero placerat erat, quis semper
      sapien nisi eu neque. Donec id maximus lacus. Proin dolor erat, tempus ac
      scelerisque fringilla, imperdiet in orci. Curabitur egestas magna ut
      mollis sollicitudin. Sed nec pulvinar eros. Donec porta tempor convallis.
      Aliquam erat volutpat. Nulla facilisi. Aenean faucibus ipsum sit amet
      dictum lobortis. Cras congue magna sapien, et facilisis arcu efficitur
      vitae. Integer nec tellus nec lectus molestie tristique. Vestibulum a sem
      aliquam, cursus erat ac, luctus lectus. Pellentesque et augue facilisis,
      ullamcorper ante at, facilisis nibh. Mauris placerat ut sapien ac pretium.
      Fusce maximus dignissim diam quis blandit. Aliquam eget ultrices velit.
    </Box>
  );
}

function SourceBox({ content }: { content: string }) {
  // on click show modal of the document
  const [openModal, changeModal] = useState(false);
  const toggleModal = () => {
    changeModal(!openModal);
  };
  return (
    <>
      <Modal isOpen={openModal} onClose={toggleModal}>
        <ModalOverlay />
        <ModalContent maxH="3000px" maxW="1500px" overflow="scroll">
          <ModalHeader>Modal Title</ModalHeader>
          <ModalCloseButton />
          <ModalContent>
            <SourceModal />
          </ModalContent>

          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={toggleModal}>
              Close
            </Button>
            <Button variant="ghost">Secondary Action</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      <Box
        width="95%"
        margin="5px"
        border="solid"
        borderColor="oklch(92.83% 0.01 286.37)"
        borderRadius="10px"
        borderWidth="1px"
        height="100px"
        padding="10px"
        onClick={toggleModal}
      >
        {content}
      </Box>
    </>
  );
}

function ContextSources() {
  // TODO: generate sources from some list of soruce objects
  return (
    <VStack
      divider={<StackDivider borderColor="gray.200" />}
      spacing={4}
      align="stretch"
      overflowY="scroll"
      h="100vh"
    >
      <SourceBox content="Source" />
      <SourceBox content="Overflow" />
      <SourceBox content="Overflow" />
    </VStack>
  );
}

interface Message {
  role: string;
  content: string;
  key: symbol;
}

interface MessageComponentProps {
  message: Message;
  editMessage: () => {};
}

// FIX CODE TO MAKE THIS MORE DRY'Y

function MessageComponent({
  message = {
    role: "user",
    content: "",
    key: Symbol(),
  },
}: {
  message: Message;
}) {
  const { colorMode } = useColorMode();
  return (
    <Box
      width="90%"
      background={
        message.role === "user"
          ? colorMode === "light"
            ? "teal.100"
            : "teal.700"
          : colorMode === "light"
            ? "gray.200"
            : "gray.700"
      }
      borderRadius="10px"
      // maxWidth="800px"
      height="auto"
      overflow="auto"
      minHeight="100px"
      justifyContent={message.role == "user" ? "right" : "left"}
      padding="20px"
    >
      {/* enclosing the message */}
      <VStack
        // divider={<StackDivider borderColor="gray.200" />}
        spacing={4}
        // align="stretch"
        overflowY="scroll"
        justifyContent={message.role == "user" ? "right" : "left"}
      // h="100vh"
      >
        <MarkdownRenderer>{message.content}</MarkdownRenderer>
        {/* <Box width="100%" height="50px">
          {!message.role && <div>Regenerate</div>}{" "}
          {message.role && <div>Edit</div>}
        </Box> */}
      </VStack>
    </Box>
  );
}

function AwaitingMessageSkeleton({ }: {}) {
  const { colorMode } = useColorMode();
  return (
    <Box
      width="90%"
      background={colorMode === "light" ? "gray.200" : "gray.700"}
      borderRadius="10px"
      // maxWidth="800px"
      height="auto"
      overflow="auto"
      minHeight="100px"
      justifyContent={false ? "right" : "left"}
      padding="20px"
    >
      <SkeletonText
        startColor="pink.500"
        endColor="orange.500"
        mt="4"
        noOfLines={4}
        spacing="4"
        skeletonHeight="2"
      />
      {/* <Box width="100%" height="50px">
          {!message.role && <div>Regenerate</div>}{" "}
          {message.role && <div>Edit</div>}
        </Box> */}
    </Box>
  );
}
// <SkeletonText mt="4" noOfLines={4} spacing="4" skeletonHeight="2" />
function ChatBox({
  chatUrl,
  modelOptions,
}: {
  chatUrl: string;
  modelOptions: string[];
}) {
  // const [messages, setMessages] = useState<Message[]>(startingMessages);
  const [messages, setMessages] = useState<Message[]>([]);
  const [needsResponse, setResponse] = useState(false);
  const [loadingResponse, setLoadingResponse] = useState(false);
  const [selectedModel, setSelectedModel] = useState("default");
  const [userChatbox, setUserChatbox] = useState("");
  // let messages: Message[] = [];

  const getResponse = async () => {
    let chat_hist = messages.map((m) => {
      let { key, ...rest } = m;
      return rest;
    });
    console.log(`chat history`);
    console.log(chat_hist);
    const modelToSend = selectedModel === "default" ? undefined : selectedModel;
    setLoadingResponse(true);
    let result = await fetch(
      // FIXME : Add the base url instead of localhost to make it more amenable to this stuff.
      // "http://localhost/api/rag/rag_chat",
      chatUrl,
      {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
          accept: "application/json",
          // "Access-Control-Allow-Origin": "*",
          "Referrer-Policy": "no-referrer",
        },
        body: JSON.stringify({
          model: modelToSend,
          chat_history: chat_hist,
        }),
      },
    )
      .then((resp) => {
        console.log("completed request");
        setLoadingResponse(false);
        console.log(resp);
        if (resp.status < 200 || resp.status > 299) {
          console.log(`error with request:\n${resp}`);
          return "failed request";
        }
        return resp.json();
      })
      .then((data) => {
        return data;
      })
      .catch((e) => {
        console.log("error making request");
        console.log(JSON.stringify(e));
      });
    console.log(result);
    setMessages([...messages, result]);
    // let c = result.body;

    // setMessages(result);
  };

  interface msgSent {
    messageInput: string;
  }
  // TODO : Fix Horrible Buggy passing the any function
  const sendMessage = async (params: msgSent) => {
    console.log("sending message");
    console.log(`msg: ${params.messageInput}`);
    let m: Message = {
      role: "user",
      content: params.messageInput,
      key: Symbol(),
    };
    console.log(`appending message "${m.content}"`);
    if (messages.length == 0) {
      // messages = [m];
      setMessages([m]);
      console.log(messages);
    } else {
      // messages = [...messages, m];
      setMessages([...messages, m]);
      console.log(messages);
    }
    setResponse(true);
    setUserChatbox("");
  };

  /*
    with take the current message, find the message
 
  */

  // get a response every time a message is sent
  useEffect(() => {
    console.log("getting response");
    if (needsResponse) {
      getResponse();
      setResponse(false);
    }
  }, [needsResponse]);
  return (
    <>
      <VStack
        divider={<StackDivider borderColor="gray.200" />}
        spacing={4}
        flexDir="column"
        overflow="scroll"
        h="100vh"
      >
        {messages.length === 0 && (
          <Box p={5} textAlign="center" color="gray.500">
            <Text fontSize="lg" fontWeight="bold">
              Welcome to the Chatbot!
            </Text>
            <Text>
              Type your message in the input box below and press Enter to send.
            </Text>
          </Box>
        )}
        {messages.map((m: Message) => {
          return (
            <MessageComponent
              // key={m.key.toString()}
              message={m}
            />
          );
        })}
        {loadingResponse && <AwaitingMessageSkeleton />}
        <Box minHeight="300px" width="100%" color="red" />
      </VStack>
      <Form onSubmit={sendMessage}>
        <FormLayout>
          <Box
            display="flex"
            flexDir="row"
            justifySelf="center"
            justifyContent="center"
            w="85%"
            borderColor="green"
            borderRadius="10px"
            borderWidth="1px"
            position="absolute"
            bottom="0"
          >
            <Field
              name="messageInput"
              type="text"
              placeholder="chat..."
              // flex-grow="2"
              paddingLeft="20px"
              resize="none"
              border="none"
              padding="10px"
              margin="10px"
              // onKeyPress={(event) => {
              //   if (event.key === 'Enter') {
              //     event.preventDefault();
              //     this.myFormRef.requestSubmit();
              //   }
              // }}
              value={userChatbox}
              // FIXME : Figure out the proper type for this
              onChange={(e: any) => setUserChatbox(e.targetvalue)}
            />
            <Center padding="10px">
              <IconButton
                isRound={true}
                variant="solid"
                colorScheme="green"
                aria-label="Send"
                type="submit"
                icon={<FiArrowUpCircle />}
              />
            </Center>
            <Select
              placeholder="default"
              onChange={(e) => setSelectedModel(e.target.value)}
              margin="10px"
              size="sm" // Adjust size to make it smaller
              width="150px" // Adjust width as needed
            >
              {modelOptions.map((model: string) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </Select>
          </Box>
        </FormLayout>
      </Form>
    </>
  );
}
/*
 */
function ChatUI({
  convoID = "",
  chatUrl,
  modelOptions,
}: {
  convoID?: string;
  chatUrl: string;
  modelOptions: string[];
}) {
  // convoId being empty is a new chat instance

  return (
    <Center width="100%" height="100%">
      <Box
        border="solid"
        borderColor="oklch(92.83% 0.01 286.37)"
        borderRadius="10px"
        borderWidth="1px"
        width="95%"
        height="95vh"
        margin="20px"
        padding="20px"
        justifySelf="center"
        overflow="clip"
        position="relative"
      >
        <Grid h="100%" gridTemplateColumns={"5fr"} gap={5}>
          <GridItem
            rowSpan={10}
            colSpan="auto"
            overflow="scroll clip"
            position="relative"
          >
            <ChatBox chatUrl={chatUrl} modelOptions={modelOptions} />
          </GridItem>

          {/* <GridItem rowSpan={10} overflow="scroll clip">
            <ContextSources />
          </GridItem> */}
        </Grid>
      </Box>
    </Center>
  );
}

export default ChatUI;

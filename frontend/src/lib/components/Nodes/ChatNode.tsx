import { useCallback, useState } from "react";
import { Handle, Position } from "reactflow";
import { Avatar, List } from "antd";

import axios from "axios";

import { message } from "antd";

import { ThreeDots } from "react-loader-spinner";

const handleStyle = { left: 10 };

import human_logo from "./../../assets/person.svg";
import ai_logo from "./../../assets/neural-net.svg";
import system_logo from "./../../assets/terminal.svg";
import { FaQuestion } from "react-icons/fa";
import { shallow } from "zustand/shallow";

import { IoIosSend } from "react-icons/io";

import "./chat-node.css";

import UseGraphStore, { GraphState } from "../../utils/GraphUtilities";

function get_chat_info(role: string, model_name: string) {
  if (role == "system") {
    return [system_logo, "System:"];
  }
  if (role == "human") {
    return [human_logo, "You:"];
  }
  if (role == "ai" || role == "assistant") {
    return [ai_logo, model_name + ":"];
  }
  return [<FaQuestion />, "Unknown:"];
}

const selector = (state: GraphState) => ({
  setNodeData: state.setNodeData,
});

type ChatNodeProps = {
  id: string;
  // TODO: define this data
  data: any;
  isConnectable: boolean;
};

function ChatNode({ id, data, isConnectable }: ChatNodeProps) {
  const { setNodeData } = UseGraphStore(selector, shallow);

  const [inputValue, setInputValue] = useState("");
  const [generatingResponse, setGeneratingResponse] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  function handleInputChange(event: React.ChangeEvent<HTMLTextAreaElement>) {
    const value = event.currentTarget.value;
    setInputValue(value);
  }
  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent the default action to avoid newline in textarea
      const formData = new FormData();
      formData.append("msg", inputValue);
      addUserChatMsg(formData);
    }
  }

  function appendChatMsg(message: any) {
    let newdata = data;
    newdata.chat_history.push(message);
    setNodeData(id, newdata);
  }

  const createLLMErrorMessage = () => {
    messageApi.open({
      type: "error",
      content: "This is an error message",
    });
  };
  const generateChatCompletion = async (
    chat_history: object[],
    model_name: string,
  ) => {
    try {
      const { data, status } = await axios.post(
        // TODO : Set up some way to have this not be hardcoded in the future and rely on tailscale
        "http://uttu-fedora:5000/v0/utils/chat_completion",
        {
          messages: chat_history,
          model: model_name,
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
          timeout: 30000, // 30 Second timeout
        },
      );
      if (status === 200) {
        console.log("Request succeeded");
        console.log(data);
        const response_message = data.response.message;
        console.log(response_message);
        appendChatMsg(response_message);
        setGeneratingResponse(false);
      } else {
        console.log(`Request failed with status ${status}:\n data: ${data}`);
        createLLMErrorMessage();
      }
    } catch (error: any) {
      // handle error
      if (error.code === "ECONNABORTED") {
        console.error("Request timed out. Please try again.");
      } else {
        console.error("An error occurred:", error.message);
      }
      createLLMErrorMessage();
    }
    createLLMErrorMessage();
  };
  const addUserChatMsg = async (formData: any) => {
    const msg = formData.get("msg");
    if (msg != "") {
      let newdata = data;
      newdata.chat_history.push({ role: "human", content: msg });
      setNodeData(id, newdata);
      setInputValue("");
      setGeneratingResponse(true);
      // TODO: Code to call the server with an updated node and llm response
      generateChatCompletion(data.chat_history, data.model_name);
    }
  };
  return (
    <div className="chat-node">
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div>
        <List
          itemLayout="horizontal"
          dataSource={data.chat_history}
          renderItem={(item: any, index) => (
            <List.Item>
              <List.Item.Meta
                // TODO : Increase performance and cache the output of the chat so it isnt called multiple times
                avatar=<Avatar
                  src={get_chat_info(item.role, data.model_name)[0]}
                ></Avatar>
                title={get_chat_info(item.role, data.model_name)[1]}
                description={item.content}
              />
            </List.Item>
          )}
        />
        {generatingResponse && (
          <List>
            <List.Item>
              <List.Item.Meta
                avatar=<Avatar
                  src={get_chat_info("ai", data.model_name)[0]}
                ></Avatar>
                title={get_chat_info("ai", data.model_name)[1]}
                description={
                  <ThreeDots
                    visible={true}
                    height="30"
                    width="60"
                    color="#4fa94d"
                    radius="9"
                    ariaLabel="three-dots-loading"
                    wrapperStyle={{}}
                    wrapperClass=""
                  />
                }
              />
              {""}
            </List.Item>
          </List>
        )}
        <form action={addUserChatMsg}>
          <textarea
            name="msg"
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
          />
          <button type="submit">
            <IoIosSend />
          </button>
        </form>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        id="a"
        style={handleStyle}
        isConnectable={isConnectable}
      />
    </div>
  );
}

export default ChatNode;

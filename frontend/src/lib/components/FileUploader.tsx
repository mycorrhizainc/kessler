import React, { useState } from "react";
import {
  Box,
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Input,
  FormControl,
  FormLabel,
  useToast,
} from "@chakra-ui/react";
import { useForm } from "react-hook-form";
import axios from "axios";

const UploadFileButton: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const { register, handleSubmit, reset } = useForm();
  const toast = useToast();

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const onFolderChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFiles(event.target.files);
    }
  };

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("/api/file/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      toast({
        title: "File uploaded",
        description: `Your file ${file.name} has been uploaded successfully.`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description: `There was an error uploading your file ${file.name}.`,
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const onSubmit = async () => {
    if (!selectedFile) {
      toast({
        title: "No file selected",
        description: "Please select a file to upload.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    await uploadFile(selectedFile);
    reset();
    setSelectedFile(null);
    onClose();
  };

  const onFolderSubmit = async () => {
    if (!selectedFiles) {
      toast({
        title: "No folder selected",
        description: "Please select a folder to upload.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    for (let i = 0; i < selectedFiles.length; i++) {
      await uploadFile(selectedFiles[i]);
    }

    reset();
    setSelectedFiles(null);
    onClose();
  };

  return (
    <>
      <Button onClick={onOpen}>Upload File</Button>
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Upload File</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Tabs>
              <TabList>
                <Tab>Single File Upload</Tab>
                <Tab>Folder Upload</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <form onSubmit={handleSubmit(onSubmit)}>
                    <FormControl>
                      <FormLabel>File</FormLabel>
                      <Input
                        type="file"
                        accept="*"
                        onChange={onFileChange}
                        {...register("file")}
                      />
                    </FormControl>
                  </form>
                </TabPanel>
                <TabPanel>
                  <form onSubmit={handleSubmit(onFolderSubmit)}>
                    <FormControl>
                      <FormLabel>Folder</FormLabel>
                      <Input
                        type="file"
                        webkitdirectory="true"
                        directory="true"
                        onChange={onFolderChange}
                        {...register("folder")}
                      />
                    </FormControl>
                  </form>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={handleSubmit(onSubmit)}>
              Upload
            </Button>
            <Button
              colorScheme="blue"
              mr={3}
              onClick={handleSubmit(onFolderSubmit)}
            >
              Upload Folder
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default UploadFileButton;

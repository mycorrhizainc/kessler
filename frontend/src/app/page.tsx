"use client";
// components
import ToolBar from "../lib/components/ToolBar";
import Layout from "../lib/components/AppLayout";

// utils
import { AddLink } from "../lib/api/files/requests";

// mui
import Textarea from "@mui/joy/Textarea";
import Button from "@mui/joy/Button";
import Alert from "@mui/joy/Alert";

// mui icons
import Add from "@mui/icons-material/Add";

import Box from "@mui/joy/Box";
import { useState } from "react";

const AddResourceComponent = () => {
  const [buttonLoading, setButtonLoad] = useState(false);
  const [hasError, setError] = useState(false);
  const [errorText, setErrorText] = useState(
    "there was an issue processing your request"
  );
  const [success, setSuccess] = useState(false);

  const notifyOfSuccessfulSubmission = () => {
    setSuccess(true);
    setTimeout(() => {
      setSuccess(false);
    }, 5000);
  };

  const notifyOfErrorSubmission = (text?: string) => {
    let old = errorText;
    if (typeof text !== "undefined") {
      setErrorText(text);
    }
    setError(true);
    setTimeout(() => {
      setError(false);
      setErrorText(old);
    }, 3000);
  };

  const handleLinkSubmission = (e: any) => {
    e.preventDefault();
    console.log("handling submission");
    setButtonLoad(true);
    // Prevent the browser from reloading the page
    const form = e.currentTarget;

    const formElements = form.elements as typeof form.elements & {
      linkText: { value: string };
    };

    const linkText = formElements.linkText.value;
    setTimeout(() => {
      setButtonLoad(false);
      notifyOfSuccessfulSubmission();
    }, 300);
    // notifyOfErrorSubmission();
    // validate that the link is valid
  };

  return (
    <div className="flex place-content-center resourceComponent container">
      {/* card container */}
      <Box
        className="flex flex-col justify-self-center max-w-50 w-3/4 p-10 space-y-5"
        sx={{
          borderRadius: "12px",
          background: "white",
        }}
      >
        <form
          method="post"
          className="space-y-5"
          onSubmit={handleLinkSubmission}
        >
          <Textarea
            name="linkText"
            minRows={2}
            color="success"
            variant="outlined"
            placeholder="add a link..."
          />
          <Button
            startDecorator={<Add />}
            loading={buttonLoading}
            loadingPosition="start"
            color="success"
            type="submit"
          >
            AddLink
          </Button>
        </form>
        {hasError && <Alert color="danger">{errorText}</Alert>}
        {success && <Alert color="success">Link Submitted!</Alert>}
      </Box>
    </div>
  );
};

export default function Home() {
  return (
    <Layout>
      <AddResourceComponent />
    </Layout>
  );
}

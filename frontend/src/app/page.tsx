"use client";
// components
<<<<<<< HEAD
import Layout from "../lib/components/AppLayout";
import LinksView from "../lib/components/ResourceList";
=======
import ToolBar from "../lib/components/ToolBar";
import Layout from "../lib/components/AppLayout";
>>>>>>> fb33946 (fixed frontend spacing, added link form)

// utils
import { AddLink } from "../lib/api/files/requests";

// mui
import Textarea from "@mui/joy/Textarea";
import Button from "@mui/joy/Button";
import Alert from "@mui/joy/Alert";
<<<<<<< HEAD
import Divider from "@mui/material/Divider";
import SvgIcon from "@mui/joy/SvgIcon";
import { styled } from "@mui/joy";
=======
>>>>>>> fb33946 (fixed frontend spacing, added link form)

// mui icons
import Add from "@mui/icons-material/Add";

import Box from "@mui/joy/Box";
<<<<<<< HEAD
import { useEffect, useState } from "react";
import axios from "axios";
import type { FileType } from "../lib/interfaces";

const VisuallyHiddenInput = styled("input")`
  clip: rect(0 0 0 0);
  clip-path: inset(50%);
  height: 1px;
  overflow: hidden;
  position: absolute;
  bottom: 0;
  left: 0;
  white-space: nowrap;
  width: 1px;
`;
=======
import { useState } from "react";
>>>>>>> fb33946 (fixed frontend spacing, added link form)

const AddResourceComponent = () => {
  const [buttonLoading, setButtonLoad] = useState(false);
  const [hasError, setError] = useState(false);
<<<<<<< HEAD

  const [links, setLinks] = useState<FileType[]>([]);

=======
>>>>>>> fb33946 (fixed frontend spacing, added link form)
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
<<<<<<< HEAD
  const getAllLinks = async () => {
    let result = await fetch("/api/files/all", {
      method: "get",
      headers: {
        Accept: "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    })
      .then((e) => {
        return e.json();
      })
      .then((e) => {
        setLinks(e);
      })
      .catch((e) => {
        console.log("error getting links:\n", e);
        return e;
      });
  };

  const handleLinkSubmission = async (e: any) => {
=======

  const handleLinkSubmission = (e: any) => {
>>>>>>> fb33946 (fixed frontend spacing, added link form)
    e.preventDefault();
    console.log("handling submission");
    setButtonLoad(true);
    // Prevent the browser from reloading the page
    const form = e.currentTarget;

    const formElements = form.elements as typeof form.elements & {
      linkText: { value: string };
    };

    const linkText = formElements.linkText.value;
<<<<<<< HEAD

    const isValidUrl = (urlString: string) => {
      var urlPattern = new RegExp(
        "^(https?:\\/\\/)?" + // validate protocol
          "((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|" + // validate domain name
          "((\\d{1,3}\\.){3}\\d{1,3}))" + // validate OR ip (v4) address
          "(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*" + // validate port and path
          "(\\?[;&a-z\\d%_.~+=-]*)?" + // validate query string
          "(\\#[-a-z\\d_]*)?$",
        "i"
      ); // validate fragment locator
      return urlPattern.test(urlString);
    };

    if (!isValidUrl(linkText)) {
      setButtonLoad(false);
      notifyOfErrorSubmission("invalid link");
      return;
    }

    const result = await AddLink(linkText);
    console.log("result from adding link", result);

    if (result == null) {
      setTimeout(() => {
        setButtonLoad(false);
        notifyOfSuccessfulSubmission();
        getAllLinks();
      }, 3000);
    }
    notifyOfErrorSubmission(result);
    setButtonLoad(false);
  };

  // update the user list every 5 sec
  useEffect(() => {
    const interval = setInterval(() => {
      getAllLinks();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col resourceComponent container space-y-10">
      {/* card container */}
      <h1 className="place-self-center text-lg">Add A Resource</h1>
      <Box
        className="flex flex-col place-self-center justify-self-center content-center max-w-50 w-3/4 p-16 space-y-5"
=======
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
>>>>>>> fb33946 (fixed frontend spacing, added link form)
        sx={{
          borderRadius: "12px",
          background: "white",
        }}
      >
        <form
          method="post"
          className="space-y-5 flex flex-col"
          onSubmit={handleLinkSubmission}
        >
          <h3>Add A Link</h3>
          <Textarea
            name="linkText"
            minRows={1}
            color="success"
            variant="outlined"
            placeholder="add a link..."
          />
          <Divider />
          <Button
            component="label"
            role={undefined}
            tabIndex={-1}
            variant="outlined"
            color="neutral"
            startDecorator={
              <SvgIcon>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z"
                  />
                </svg>
              </SvgIcon>
            }
          >
            Upload a file
            <VisuallyHiddenInput type="file" name="fileUpload" id="upload" />
          </Button>
          <br />
          <Button
            className="place-self-center max-w-40"
            startDecorator={<Add />}
            loading={buttonLoading}
            loadingPosition="start"
            color="success"
            type="submit"
          >
            Add Resource
          </Button>
        </form>
        {hasError && <Alert color="danger">{errorText}</Alert>}
        {success && <Alert color="success">Link Submitted!</Alert>}
      </Box>
      <Box
        className="flex flex-col place-self-center max-w-50 w-3/4 p-16 space-y-5"
        sx={{
          borderRadius: "12px",
          background: "white",
        }}
      >
        <LinksView links={links} getAllLinks={getAllLinks} />
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

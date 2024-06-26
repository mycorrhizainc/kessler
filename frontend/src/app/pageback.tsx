// @ts-nocheck
// FIXME : Enable ts type checking once it is working
"use client";
// components
import Layout from "../lib/components/AppLayout";
import LinksView from "../lib/components/ResourceList";

// utils
import AddLink from "../lib/requests";

// mui
import Textarea from "@mui/joy/Textarea";
import Button from "@mui/joy/Button";
import Alert from "@mui/joy/Alert";
import Divider from "@mui/material/Divider";
import SvgIcon from "@mui/joy/SvgIcon";
import { styled } from "@mui/joy";

// mui icons
import Add from "@mui/icons-material/Add";

import Box from "@mui/joy/Box";
import { useEffect, useState } from "react";
import axios from "axios";
import type { FileType } from "../lib/interfaces";

// clerk
import { useAuth } from "@clerk/nextjs";
import AuthenticatedFetch from "../lib/requests";

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

const AddResourceComponent = () => {
  const [buttonLoading, setButtonLoad] = useState(false);
  const [hasError, setError] = useState(false);
  // const { getToken } = useAuth();

  const [links, setLinks] = useState<FileType[]>([]);

  // FIXME : Tried removing from block and got error with setlinks, just removed the export statement.
  const getAllFiles = async () => {
    const authfetch = AuthenticatedFetch();
    let result = await authfetch("/api/files/all", {
      method: "get",
      headers: {
        Accept: "application/json",
        // Authorization: `Bearer ${await getToken()}`,
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
  const [errorText, setErrorText] = useState(
    "there was an issue processing your request",
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

  const handleLinkSubmission = async (e: any) => {
    e.preventDefault();
    console.log("handling submission");
    setButtonLoad(true);
    // Prevent the browser from reloading the page
    const form = e.currentTarget;

    const formElements = form.elements as typeof form.elements & {
      linkText: { value: string };
    };

    const linkText = formElements.linkText.value;

    const isValidUrl = (urlString: string) => {
      var urlPattern = new RegExp(
        "^(https?:\\/\\/)?" + // validate protocol
          "((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|" + // validate domain name
          "((\\d{1,3}\\.){3}\\d{1,3}))" + // validate OR ip (v4) address
          "(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*" + // validate port and path
          "(\\?[;&a-z\\d%_.~+=-]*)?" + // validate query string
          "(\\#[-a-z\\d_]*)?$",
        "i",
      ); // validate fragment locator
      return urlPattern.test(urlString);
    };

    if (!isValidUrl(linkText)) {
      setButtonLoad(false);
      notifyOfErrorSubmission("invalid link");
      return;
    }

    // FIXME:  Seemed to not 0 arguments instead of one argument
    // const result = await AddLink(linkText);
    const result = await AddLink();
    console.log("result from adding link", result);

    if (result == null) {
      setTimeout(() => {
        setButtonLoad(false);
        notifyOfSuccessfulSubmission();
        // FIXME : Uncomment
        // getAllLinks();
      }, 3000);
    }
    // FIXME : Type error
    // notifyOfErrorSubmission(result);
    setButtonLoad(false);
  };

  // update the user list every 5 sec
  useEffect(() => {
    const interval = setInterval(() => {
      // getAllLinks();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col resourceComponent container space-y-10">
      {/* card container */}
      <h1 className="place-self-center text-lg">Add A Resource</h1>
      <Box
        className="flex flex-col place-self-center justify-self-center content-center max-w-50 w-3/4 p-16 space-y-5"
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

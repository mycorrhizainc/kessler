"use client";
import { useEffect, useState } from "react";
import axios from "axios";
import { link } from "fs";
import { stringify } from "querystring";
import ToolBar from "../../lib/components/ToolBar";
import Layout from "../../lib/components/AppLayout";

type LinkData = {
  date_created: string;
  url: string;
  id: string;
  title: string;
};

const AddLink = ({ refreshList }: { refreshList: () => void }) => {
  const [link, setLink] = useState("");

  const PostLink = async (formData: any) => {
    console.log(`link:\n${link}`);

    await fetch("/api/files", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        "Access-Control-Allow-Origin": "*",
      },
      body: JSON.stringify({ url: link }),
    })
      .then((e) => {
        console.log(`successfully added link "${link}":\n${e}`);
      })
      .then(() => {
        refreshList();
      })
      .catch((e) => {
        console.log(`error adding links:\n${e}`);
      });
  };

  return (
    <div className="link-container" id="link-add">
      <form action={PostLink}>
        <input
          type="text"
          name="link"
          value={link}
          onChange={(e) => setLink(e.target.value)}
        />
        <button type="submit">Send Link</button>
      </form>
    </div>
  );
};

const LinksView = () => {
  let ul: any[] = [];
  let [links, setLinks] = useState<any[]>([]);
  const getAllLinks = () => {
    let l = axios
      .get("/api/files/all")
      .then((e) => {
        setLinks(e.data);
      })
      .catch((err) => console.log(err));
  };
  useEffect(() => {
    getAllLinks();
  }, []);
  const items = links.map((link) => {
    return (
      <li key={link.url}>
        <a href={link.url}>{link.url}</a>
      </li>
    );
  });
  return (
    <Layout>
      <div>
        <h1>Links</h1>
        {links.length > 0 && <ul>{items}</ul>}
        {links.length == 0 && <>No Links</>}
      </div>
      <br />
      <>
        <AddLink refreshList={getAllLinks} />
      </>
    </Layout>
  );
};

export default LinksView;

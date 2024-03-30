import axios from "axios";
import Layout from "./AppLayout";
import { useEffect } from "react";

type LinksViewProps = {
  links: any[];
  getAllLinks: () => void;
};

const LinksView = ({ links, getAllLinks }: LinksViewProps) => {
  useEffect(() => {
    getAllLinks();
  }, []);
  const items = links.map((link) => {
    return (
      <li key={link.id}>
        <a href={link.url}>{link.url}</a>
      </li>
    );
  });
  return (
    <div>
      <h1>Links</h1>
      {links.length > 0 && <ul>{items}</ul>}
      {links.length == 0 && <>No Links</>}
    </div>
  );
};

export default LinksView;

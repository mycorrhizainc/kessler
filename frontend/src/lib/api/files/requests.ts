const AddLocalFile = () => {};
const DeleteLocalFile = () => {};

export const AddLink = async (link: string): Promise<any> => {
  console.log(`link:\n${link}`);

  let result = await fetch("/api/files/add", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      "Access-Control-Allow-Origin": "*",
    },
    body: JSON.stringify({ url: link, title: "Textual content", isUrl: true }),
  })
    .then((e) => {
      if (e.status < 200 || e.status > 299) {
        console.log(`error adding links:\n${e}`);
        return "failed request";
      }
      console.log(`successfully added link "${link}":\n${e}`);
      return null;
    })
    .catch((e) => {
      console.log(`error adding links:\n${e}`);
      return e;
    });
  return result;
};
const RemoveLink = () => {};

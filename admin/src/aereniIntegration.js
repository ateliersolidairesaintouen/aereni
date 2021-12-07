import { fetchUtils } from "react-admin";
import { stringify } from "query-string";

const apiUrl = process.env.REACT_APP_AERENI_API_URL;
const httpClient = fetchUtils.fetchJson;

function buildHeaders() {
  const username = localStorage.getItem("username");
  const password = localStorage.getItem("password");

  let headers = new Headers();
  if (username && password) {
    headers.set(
      "Authorization",
      "Basic " + Buffer.from(username + ":" + password).toString("base64")
    );
  }

  return headers;
}

function sortBy(field, order) {
  return (a,b) => (a[field] > b[field]) ? (order === "ASC" ? 1 : -1) : ((b[field] > a[field]) ? (order === "ASC" ? -1 : 1) : 0)
}


export const authProvider = {
  login: ({ username, password }) => {
    localStorage.setItem("username", username);
    localStorage.setItem("password", password);
    return Promise.resolve();
  },
  checkError: (error) => {
    const status = error.status;
    if (status === 401 || status === 403) {
      localStorage.removeItem("username");
      localStorage.removeItem("password");
      return Promise.reject();
    }
    // other error code (404, 500, etc): no need to log out
    return Promise.resolve();
  },
  checkAuth: (params) => {
    return httpClient(`${apiUrl}/stations`, {
      method: "GET",
      headers: buildHeaders(),
    });
  },
  logout: () => {
    localStorage.removeItem("username");
    localStorage.removeItem("password");
    return Promise.resolve();
  },
  getIdentity: () => Promise.resolve(),
  // authorization
  getPermissions: (params) => Promise.resolve(),
};

export const dataProvider = {
  getList: (resource, params) => {
    const { page, perPage } = params.pagination;
    const { field, order } = params.sort;
    const query = {
      sort: JSON.stringify([field, order]),
      range: JSON.stringify([(page - 1) * perPage, page * perPage - 1]),
      filter: JSON.stringify(params.filter),
    };
    const url = `${apiUrl}/${resource}?${stringify(query)}`;


    console.log(params)

    return httpClient(url, { method: "GET", headers: buildHeaders() }).then(
      ({ headers, json }) => ({
        data: json.sort(sortBy(field, order)),
        total: parseInt(headers.get("x-total-count"), 10),
      })
    );
  },

  getOne: (resource, params) =>
    httpClient(`${apiUrl}/${resource}/${params.id}`, {
      method: "GET",
      headers: buildHeaders(),
    }).then(({ json }) => ({
      data: json,
    })),

  getMany: (resource, params) => {
    throw new Error("getMany not implemented");
  },

  getManyReference: (resource, params) => {
    throw new Error("getManyReference not implemented");
  },

  update: (resource, params) =>
    httpClient(`${apiUrl}/${resource}/${params.id}`, {
      method: "PATCH",
      headers: buildHeaders(),
      body: JSON.stringify(params.data),
    }).then(({ json }) => ({ data: json })),

  updateMany: (resource, params) => {
    throw new Error("updateMany not implemented");
  },

  create: (resource, params) =>
    httpClient(`${apiUrl}/${resource}`, {
      method: "POST",
      headers: buildHeaders(),
      body: JSON.stringify(params.data),
    }).then(({ json }) => ({
      data: { ...params.data, aereni_id: json.id },
    })),

  delete: (resource, params) =>
    httpClient(`${apiUrl}/${resource}/${params.id}`, {
      method: "DELETE",
      headers: buildHeaders(),
    }).then(({ json }) => ({ data: json })),

  deleteMany: (resource, params) => {
    return Promise.all(
      params.ids.map((id) =>
        httpClient(`${apiUrl}/${resource}/${id}`, {
          method: "DELETE",
          headers: buildHeaders(),
        })
      )
    ).then(({ values }) => ({ data: [] }));
  },
};

// in src/App.js
import * as React from "react";
import {
  Admin,
  Resource,
  List,
  Datagrid,
  TextField,
  NumberField,
  BooleanField,
  Edit,
  SimpleForm,
  TextInput,
  NumberInput,
  BooleanInput,
  Create
} from "react-admin";
import {dataProvider, authProvider} from "./aereniIntegration";

const StationList = (props) => (
  <List {...props}>
    <Datagrid rowClick="edit">
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="owner" />

      <TextField source="esp_id" />
      <TextField source="sensebox_id" />

      <TextField source="node_id" />
      <TextField source="user" />
      <TextField source="address" />
      <NumberField source="lat" />
      <NumberField source="lon" />
      <NumberField source="floor" />
      <BooleanField source="indoor" />

      <BooleanField source="production" />
      <TextField multiline source="comment" />
    </Datagrid>
  </List>
);

export const StationEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="id" />
      <TextInput source="name" />
      <TextInput source="owner" />

      <TextInput source="esp_id" />
      <TextInput source="sensebox_id" />

      <TextInput source="node_id" />
      <TextInput source="user" />
      <TextInput source="address" />
      <NumberInput source="lat" />
      <NumberInput source="lon" />
      <NumberInput source="floor" />
      <BooleanInput source="indoor" />

      <BooleanInput source="production" />
      <TextInput multiline source="comment" />
    </SimpleForm>
  </Edit>
);

export const StationCreate= (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="id" />
      <TextInput source="name" />
      <TextInput source="owner" />

      <TextInput source="esp_id" />
      <TextInput source="sensebox_id" />

      <TextInput source="node_id" />
      <TextInput source="user" />
      <TextInput source="address" />
      <NumberInput source="lat" />
      <NumberInput source="lon" />
      <NumberInput source="floor" />
      <BooleanInput source="indoor" />

      <BooleanInput source="production" />
      <TextInput source="comment" />
    </SimpleForm>
  </Create>
);

const App = () => (
  <Admin dataProvider={dataProvider} authProvider={authProvider}>
    <Resource name="stations" list={StationList} edit={StationEdit} create={StationCreate}/>
  </Admin>
);

export default App;

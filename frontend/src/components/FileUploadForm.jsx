import React, { useState } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function getFileExtension(fileName) {
  return fileName.slice((fileName.lastIndexOf(".") - 1 >>> 0) + 2);
}

const FileUploadForm = () => {
    const [formData, setFormData] = useState({
      title: '',
      image: null,
      file_3d: null,
    });
  
    const handleChange = (e) => {
      const { name, value, files } = e.target;
      setFormData({
        ...formData,
        [name]: files ? files[0] : value,
      });
    };

    const validateSubmitData = (submitData) => {
      let allowedImgExtension = ["jpg", "png"];
      let allowedFileExtension = ["glb", "obj"];
      let error = "";

      if (submitData.title != "" && submitData.image != "" && submitData.file_3d != "") {
        let img_extension = getFileExtension(submitData.image["name"])
        let model_extension = getFileExtension(submitData.file_3d["name"])
        if (allowedImgExtension.includes(img_extension)) {
          if (allowedFileExtension.includes(model_extension)) {
            return true
          }
          else {
            error = "The file format of the 3D file is invalid."
          }
        }
        else {
          error = "The file format of the image is invalid."
        }
      }
      else {
        error = "There is an empty field."
      }
      
      toast.error(error);
      return false
    }
  
    const handleSubmit = (e) => {
      e.preventDefault();
  
      if(!validateSubmitData(formData)) {
        return;
      };

      const apiUrl = 'http://127.0.0.1:8000/api/uploaded-files/';
      const formDataToSend = new FormData();

      formDataToSend.append('title', formData.title);
      formDataToSend.append('image', formData.image);
      formDataToSend.append('file_3d', formData.file_3d);

  
      fetch(apiUrl, {
        method: 'POST',
        body: formDataToSend,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Success:', data);
          toast.success('Request successful!');
        })
        .catch((error) => {
          console.error('Error:', error);
          toast.error(error);
        });
    };
  
    return (
      <form className="max-w-xl mx-auto mt-8" onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
            Title
          </label>
          <input
            type="text"
            id="title"
            name="title"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Enter your title"
            value={formData.title}
            onChange={handleChange}
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="image">
            Image
          </label>
          <input
            type="file"
            id="image"
            name="image"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            onChange={handleChange}
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="file_3d">
            3D File
          </label>
          <input
            type="file"
            id="file_3d"
            name="file_3d"
            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            onChange={handleChange}
            required
          />
        </div>
        <button
          type="submit"
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
        >
          Submit
        </button>
      </form>
    );
  };
  
  export default FileUploadForm;
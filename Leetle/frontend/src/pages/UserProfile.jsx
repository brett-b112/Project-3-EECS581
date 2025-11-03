import React from 'react';

const UserProfile = () => {
  return (
    <div className="container mx-auto mt-10">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center">
          <div>
            <h2 className="text-2xl font-bold">User 1</h2>
            <p className="text-gray-600">user1@ku.edu</p>
          </div>
        </div>
        <div className="mt-6">
          <h3 className="text-lg font-semibold">About Me</h3>
          <p className="text-gray-700 mt-2">
            Hello! I'm User 1, a passionate coder who loves solving problems and building
            applications. In my free time, I enjoy hiking and exploring new technologies.
          </p>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;

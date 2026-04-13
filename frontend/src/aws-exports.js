// aws-exports.js
// const awsExports = {
//   aws_project_region: import.meta.env.VITE_AWS_REGION,
//   aws_cognito_region: import.meta.env.VITE_AWS_REGION,
//   aws_user_pools_id: import.meta.env.VITE_COGNITO_USER_POOL_ID,
//   aws_user_pools_web_client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
//   oauth: {},
// };

// export default awsExports;
const awsExports = {
  Auth: {
    Cognito: {
      region: import.meta.env.VITE_AWS_REGION,
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
    },
  },
};

export default awsExports;
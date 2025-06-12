# Dockerfile

# ---- Stage 1: Build the application ----
# Use the official Node.js 20 image as a base for building.
# 'alpine' is a lightweight version of Linux.
FROM node:20-alpine AS builder

# Set the working directory inside the container.
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker layer caching.
# This step only re-runs if these files change.
COPY package*.json ./
RUN npm install

# Copy the rest of the application source code.
COPY . .

# Build the Next.js application for production.
RUN npm run build

# ---- Stage 2: Create the final production image ----
# Use a minimal Node.js image for the final container.
FROM node:20-alpine AS runner

WORKDIR /app

# Create a non-root user for security best practices.
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy the built application from the 'builder' stage.
# This includes the .next folder (standalone output), public folder, and package.json.
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json .

# Next.js in standalone mode doesn't need all node_modules, only a few.
# By running a minimal install, we keep the image size down.
RUN npm install --omit=dev --production

# Change ownership of the files to our non-root user.
RUN chown -R nextjs:nodejs .

# Switch to the non-root user.
USER nextjs

# Expose the port the app will run on.
EXPOSE 3000

# The command to start the Next.js server in production mode.
CMD ["npm", "start"]
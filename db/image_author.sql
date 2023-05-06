/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50561
 Source Host           : localhost:3306
 Source Schema         : image_sprder

 Target Server Type    : MySQL
 Target Server Version : 50561
 File Encoding         : 65001

 Date: 06/05/2023 15:07:31
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for image_author
-- ----------------------------
DROP TABLE IF EXISTS `image_author`;
CREATE TABLE `image_author`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `author_name` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '作者名称',
  `author_url` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '作者主页链接',
  `opus_url` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '作品链接',
  `uuid` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '标识',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 33240 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Compact;

SET FOREIGN_KEY_CHECKS = 1;
